import re
from typing import List, Dict, Any, Optional

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class BaselineChatbot:
    """
    Phase 1 baseline chatbot.
    - Single-turn
    - Simple routing to one tool (arxiv or pubmed)
    - Falls back to LLM if no tool is needed
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]]):
        self.llm = llm
        self.tools = {t["name"]: t["function"] for t in tools}
        self.history = []

    def _get_system_prompt(self) -> str:
        return (
            "You are a helpful research assistant. "
            "Answer clearly and concisely. "
            "If you are unsure, say so."
        )

    def _extract_arxiv_id(self, text: str) -> Optional[str]:
        # Match modern arXiv IDs like 2401.12345 or 2401.12345v2
        match = re.search(r"(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)", text, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_pmid(self, text: str) -> Optional[str]:
        # PMID is usually 6-9 digits; require pubmed/pmid context to avoid false positives
        if re.search(r"\b(pmids?|pubmed)\b", text, re.IGNORECASE):
            match = re.search(r"\b(\d{6,9})\b", text)
            return match.group(1) if match else None
        return None

    def _is_biomed_query(self, text: str) -> bool:
        biomed_keywords = [
            "biomed", "biomedical", "medicine", "medical", "clinical", "patient",
            "disease", "cancer", "tumor", "therapy", "drug", "trial", "gene",
            "protein", "cell", "pubmed", "pmid", "neuro", "immunology",
            "cardio", "covid", "vaccine"
        ]
        text_l = text.lower()
        return any(k in text_l for k in biomed_keywords)

    def _route(self, user_input: str) -> Dict[str, str]:
        text = user_input.strip()
        if not text:
            return {"tool": "", "args": "", "reason": "empty_input"}

        # Explicit prefixes
        if text.lower().startswith("arxiv:"):
            query = text.split(":", 1)[1].strip()
            return {"tool": "search_arxiv", "args": query, "reason": "explicit_arxiv"}
        if text.lower().startswith("pubmed:"):
            query = text.split(":", 1)[1].strip()
            return {"tool": "search_pubmed", "args": query, "reason": "explicit_pubmed"}

        arxiv_id = self._extract_arxiv_id(text)
        if arxiv_id:
            return {"tool": "fetch_arxiv", "args": arxiv_id, "reason": "arxiv_id"}

        pmid = self._extract_pmid(text)
        if pmid:
            return {"tool": "fetch_pubmed", "args": pmid, "reason": "pmid"}

        if self._is_biomed_query(text):
            return {"tool": "search_pubmed", "args": text, "reason": "biomed_query"}

        return {"tool": "search_arxiv", "args": text, "reason": "default_arxiv"}

    def _execute_tool(self, tool_name: str, args: str) -> str:
        tool_fn = self.tools.get(tool_name)
        if not tool_fn:
            return f"Error: Tool '{tool_name}' not found."
        try:
            return str(tool_fn(args))
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"

    def run(self, user_input: str) -> str:
        logger.log_event("BASELINE_START", {"input": user_input, "model": self.llm.model_name})

        route = self._route(user_input)
        tool_name = route["tool"]
        args = route["args"]

        if tool_name:
            result = self._execute_tool(tool_name, args)
            logger.log_event("BASELINE_TOOL", {
                "tool": tool_name,
                "args": args,
                "reason": route.get("reason", "")
            })
            return result

        # Fallback to plain LLM response
        try:
            result = self.llm.generate(user_input, system_prompt=self._get_system_prompt())
            tracker.track_request(
                provider=result.get("provider", "unknown"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0)
            )
            return result.get("content", "")
        except Exception as e:
            logger.log_event("LLM_ERROR", {"error": str(e)})
            return f"Error communicating with LLM: {str(e)}"


