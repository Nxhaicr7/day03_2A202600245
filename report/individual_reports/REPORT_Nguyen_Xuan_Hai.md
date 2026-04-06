# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Xuân Hải
- **Student ID**: 2A202600245
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: src/tools/search_pubmed.py
- **Code Highlights**: 
        # Tối ưu hóa việc gọi E-utilities API của NCBI
        search_resp = requests.get(f"{base_url}esearch.fcgi", params={
            "db": "pubmed", "term": term, "retmax": max_results, "retmode": "json"
        }, timeout=10)
        # Trích xuất DOI bằng generator expression để code ngắn gọn
        doi = next((id["value"] for id in item.get("articleids", []) if id.get("idtype") == "doi"), "")
- **Documentation**: Code được thiết kế để Agent có thể gọi thông qua cơ chế Function Calling của OpenAI. Tool nhận vào query y khoa, thực hiện quy trình 2 bước (ESearch để lấy IDs và ESummary để lấy Metadata), sau đó trả về JSON rút gọn giúp Agent dễ dàng tóm tắt trong bước Observation của vòng lặp ReAct.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent từ chối xử lý và trả về thông báo: "I can't assist with requests involving personal information" khi người dùng nhập email cá nhân.
- **Log Source**: {"event": "LLM_RESPONSE", "data": {"step": 1, "content": "I'm sorry, but I can't assist with requests involving personal information..."}}
- **Diagnosis**: Do cơ chế Safety Filter của mô hình (GPT-4o/Gemini) tự động kích hoạt khi phát hiện dữ liệu định danh cá nhân (PII) như email trong phần User Input, dẫn đến việc Agent dừng vòng lặp ReAct ngay lập tức.
- **Solution**: Điều chỉnh cách kiểm thử (Sử dụng các câu lệnh chuyên môn thay vì dữ liệu cá nhân) và cấu hình lại System Prompt để định nghĩa rõ phạm vi xử lý dữ liệu của Agent.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Khối Thought giúp Agent có thời gian "suy nghĩ" để phân tách yêu cầu phức tạp. Thay vì trả lời bừa, nó biết dừng lại để xác định mình cần dùng search_pubmed để lấy dữ liệu thực tế trước khi đưa ra kết luận y khoa.
2.  **Reliability**: Agent hoạt động kém hơn Chatbot thông thường khi gặp các câu hỏi mang tính chất riêng tư hoặc thông tin quá phổ thông, vì cấu trúc ReAct làm tăng độ trễ (latency) và dễ bị kích hoạt các bộ lọc bảo mật khắt khe hơn.
3.  **Observation**: Kết quả trả về từ môi trường (ví dụ danh sách bài báo từ PubMed) đóng vai trò là "kiến thức tạm thời". Agent dựa vào đây để điều chỉnh bước tiếp theo, nếu không có kết quả, nó sẽ tự động thay đổi từ khóa tìm kiếm (Query Refinement).

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Chuyển đổi các lời gọi API từ requests (đồng bộ) sang httpx (bất đồng bộ) để có thể xử lý hàng trăm yêu cầu tra cứu tài liệu cùng lúc.
- **Safety**: Triển khai một lớp "Guardrails" riêng biệt để kiểm tra dữ liệu đầu ra của Tool trước khi đưa lại cho LLM, đảm bảo không có mã độc hoặc thông tin sai lệch được trả về.
- **Performance**: Sử dụng Redis để lưu bộ nhớ đệm (Caching) cho các kết quả tìm kiếm PubMed phổ biến, giúp giảm chi phí gọi API và tăng tốc độ phản hồi cho người dùng.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_Nguyen_Xuan_Hai.md` and placing it in this folder.
