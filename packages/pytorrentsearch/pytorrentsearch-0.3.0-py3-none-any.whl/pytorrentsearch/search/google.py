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
        next(min_waiter)
        status("Fetching Google result page...")
        search_url = f"https://www.google.com/search?q={quote(query)}&start={(page - 1) * 20}"  # noqa: E501
        content = get_url_content(search_url)
        page_links = set()
        for link in LINK_REGEXP.findall(content):
            if link.startswith("/url"):
                if link.find("http") != -1:
                    link = link[link.find("http") :]
                else:
                    continue
                if link.find("&amp"):
                    link = link[0 : link.find("&amp")]
            if link.startswith("http") and link.find("google.com") == -1:
                page_links.add(link)
        if len(page_links) == 0:
            break
