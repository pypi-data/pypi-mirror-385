import re

LINK_REGEXP = re.compile('<a [^>]*href="([^"]*)"')


def query_results(query: str, page=1):
    from urllib.parse import quote

    from pytorrentsearch.utils import get_url_content, min_wait, status

    page_links: set[str] = set()
    min_waiter = min_wait(5)
    while True:
        for link in page_links:
            yield link
        page_links = set()
        next(min_waiter)
        status("Fetching DuckDuckGo result page...")
        search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}&s={(page - 1) * 20}"  # noqa: E501
        content = get_url_content(search_url)
        page_links = set()
        for link in LINK_REGEXP.findall(content):
            if link.startswith("http"):
                page_links.add(link)
        if len(page_links) == 0:
            break
