import requests
import xml.etree.ElementTree as ET

from src.tools.search_arxiv import fetch_arxiv, parse_arxiv_xml

ARXIV_ID_URL = "http://export.arxiv.org/api/query?id_list={paper_id}"


def fetch_arxiv_paper(paper_id: str) -> str:
    print(f"\n fetch_arxiv_paper | paper_id: '{paper_id}'")
    try:
        url    = f"http://export.arxiv.org/api/query?id_list={paper_id}"
        xml    = fetch_arxiv(url)
        papers = parse_arxiv_xml(xml)

        if not papers:
            return f"No paper found for ID: {paper_id}"

        p = papers[0]

        lines = [
            "=" * 60,
            f"Title     : {p['title']}",
            f"ArXiv ID  : {p['arxiv_id']}",
            f"Published : {p['published']}",
            f"Category  : {p['category']}",
            f"Authors   : {', '.join(p['authors'])}",
            "-" * 60,
            f"Abstract  : {p['abstract']}",
            "-" * 60,
            f"PDF       : {p['pdf_url']}",
            f"URL       : {p['abstract_url']}",
            "=" * 60,
        ]

        return "\n".join(lines)

    except requests.exceptions.Timeout:
        return "Timeout: ArXiv did not respond. Try again later."
    except requests.exceptions.ConnectionError:
        return "Connection error: check your internet."
    except requests.exceptions.HTTPError as e:
        return f"HTTP {e.response.status_code}: {str(e)}"
    except ET.ParseError as e:
        return f"XML parse error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# Tool Definition
FETCH_ARXIV_TOOL = {
    "name": "fetch_arxiv",
    "description": (
        "Fetch full details of a specific ArXiv paper by its ID. "
        "Input: a single ArXiv paper ID string, e.g. '2401.12345'. "
        "Returns title, authors, published date, category, abstract, and PDF URL. "
        "Use when you already know the ArXiv ID and need the paper's full details."
    ),
    "function": fetch_arxiv_paper,
}
