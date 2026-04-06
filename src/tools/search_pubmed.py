import requests

from src.tools.fetch_pubmed import efetch_tool

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
REQUEST_TIMEOUT = 10


def search_pubmed(query: str) -> str:
    """
    Search PubMed for papers matching a query string.

    Args:
        query: Search terms (e.g. "CRISPR gene editing 2023")

    Returns:
        Formatted string with numbered list of results, or an error message.
    """
    print(f"\n search_pubmed | query: '{query}'")

    # Step 1: Get PMIDs via esearch
    try:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 4,
            "retmode": "json",
        }
        response = requests.get(ESEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
    except requests.exceptions.Timeout:
        return "Error: PubMed esearch timed out. Try again later."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to PubMed. Check your internet connection."
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {e.response.status_code} from PubMed esearch: {str(e)}"
    except Exception as e:
        return f"Error during PubMed search: {str(e)}"

    if not id_list:
        return f"No results found on PubMed for: '{query}'"

    # Step 2: Fetch article details via efetch
    try:
        fetch_result = efetch_tool(id_list)
        articles = fetch_result.get("articles", [])
    except Exception as e:
        return f"Error fetching article details from PubMed: {str(e)}"

    if not articles:
        return f"Found {len(id_list)} PMIDs but could not retrieve article details."

    # Step 3: Format results
    lines = [f"Found {len(articles)} PubMed result(s) for '{query}':\n", "=" * 60]

    for i, article in enumerate(articles, 1):
        abstract = article.get("abstract", "")
        if len(abstract) > 300:
            abstract = abstract[:300] + "..."

        lines += [
            f"\n[{i}] {article.get('title', 'No title')}",
            f"     Journal : {article.get('journal', 'N/A')}",
            f"     PMID    : {article.get('pmid', 'N/A')}",
            f"     Abstract: {abstract if abstract else 'N/A'}",
            "-" * 60,
        ]

    print(f"   Done — {len(articles)} articles returned")
    return "\n".join(lines)


SEARCH_PUBMED_TOOL = {
    "name": "search_pubmed",
    "description": (
        "Search PubMed for biomedical and life-science research papers. "
        "Input: a search query string (e.g. 'COVID-19 mRNA vaccine efficacy'). "
        "Returns titles, journals, PMIDs, and abstracts. "
        "Use for medical, clinical, or biology research topics."
    ),
    "function": search_pubmed,
}
