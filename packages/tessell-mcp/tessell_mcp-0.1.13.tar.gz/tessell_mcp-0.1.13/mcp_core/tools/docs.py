import logging
import requests
from mcp_core.mcp_server import mcp

logger = logging.getLogger(__name__)

DOCS_SEARCH_URL = "https://n6cd32iwzheix3ibmqgfn5jn3a0hjnhx.lambda-url.us-east-2.on.aws/"
# DOCS_SEARCH_TOKEN is an additional layer of safety at the lambda side to prevent casual abuse
DOCS_SEARCH_TOKEN = "Nagzik#xuwkas$-baqwo6"

@mcp.tool()
def docs_search(query: str):
    """
    Search documentation using the Tessell docs search endpoint. When responding to the user, include all applicable documentation URLs (one or more) from the response if they are relevant to the query.

    Args:
        query (str): The search query string.
    Returns:
        dict: The response from the documentation search API, including status code and content.
    """
    logger.info(f"Searching docs with query: {query}")
    try:
        headers = {"x-docs-token": DOCS_SEARCH_TOKEN}
        resp = requests.get(DOCS_SEARCH_URL, params={"query": query}, headers=headers, timeout=10)
        logger.info(f"Docs search status_code={resp.status_code}")
        return {"status_code": resp.status_code, "content": resp.text}
    except Exception as e:
        logger.exception("Docs search failed.")
        return {"status_code": 500, "error": str(e)} 