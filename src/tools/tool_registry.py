"""
Tool registry — wraps all tool implementations into the standard dict format
expected by ReActAgent: {"name": str, "description": str, "function": callable}

Every function signature: def fn(args: str) -> str
"""

from datetime import datetime
from src.tools.search_arxiv import search_arxiv
from src.tools.search_pubmed import search_pubmed
from src.tools.fetch_pubmed import efetch_tool
from src.tools.tavily_search import tavily_search
from src.tools.tavily_extract import TavilyExtractTool


# --- Wrappers ---

def _get_current_date(args: str) -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _search_tavily(query: str) -> str:
    urls = tavily_search(query)
    if not urls:
        return "No results found."
    return "\n".join(f"- {url}" for url in urls)


_extractor = None

def _fetch_tavily(url: str) -> str:
    global _extractor
    if _extractor is None:
        _extractor = TavilyExtractTool()
    result = _extractor.extract(url.strip(), summarize=True)
    if not result.results:
        return "No content extracted."
    return result.results[0].preview(max_chars=1000)


def _fetch_pubmed(pmid: str) -> str:
    """Wrapper: takes a single PMID string, returns formatted article details."""
    pmid = pmid.strip()
    if not pmid:
        return "Error: No PMID provided."
    try:
        result = efetch_tool([pmid])
        articles = result.get("articles", [])
        if not articles:
            return f"No article found for PMID: {pmid}"
        a = articles[0]
        abstract = a.get("abstract", "N/A")
        return (
            f"Title   : {a.get('title', 'N/A')}\n"
            f"Journal : {a.get('journal', 'N/A')}\n"
            f"PMID    : {a.get('pmid', 'N/A')}\n"
            f"Abstract: {abstract}"
        )
    except Exception as e:
        return f"Error fetching PubMed article: {str(e)}"


# --- Tool Definitions ---

TOOLS = [
    {
        "name": "get_current_date",
        "description": "Get the current date. Args: none",
        "function": _get_current_date,
    },
    {
        "name": "search_tavily",
        "description": (
            "Search the web for a broad overview of a topic. "
            "Returns a list of relevant URLs. "
            "Args: query (str). Example: 'latest research on LLM agents'"
        ),
        "function": _search_tavily,
    },
    {
        "name": "fetch_tavily",
        "description": (
            "Fetch and summarize the content of a URL. "
            "Use after search_tavily to read a specific page. "
            "Args: url (str). Example: 'https://example.com/article'"
        ),
        "function": _fetch_tavily,
    },
    {
        "name": "search_arxiv",
        "description": (
            "Search for scientific papers on ArXiv. "
            "Simple input: 'RAG language model 2024'. "
            "Advanced: 'ti:attention AND au:vaswani'. "
            "Use for CS/AI/ML academic papers."
        ),
        "function": search_arxiv,
    },
    {
        "name": "search_pubmed",
        "description": (
            "Search PubMed for biomedical and life-science research papers. "
            "Args: query (str). Example: 'CRISPR gene therapy'"
        ),
        "function": search_pubmed,
    },
    {
        "name": "fetch_pubmed",
        "description": (
            "Fetch full details of a PubMed article by its PMID. "
            "Args: PMID (str). Example: '38012345'"
        ),
        "function": _fetch_pubmed,
    },
]
