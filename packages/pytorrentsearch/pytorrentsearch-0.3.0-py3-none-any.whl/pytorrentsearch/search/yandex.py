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
        status("Fetching Yandex result page...")
        search_url = f"https://yandex.com/search?text={quote(query)}&p={page}"
        content = get_url_content(search_url)
        page_links = set()
        for link in LINK_REGEXP.findall(content):
            # if link.startswith("http"):
            page_links.add(link)
        if len(page_links) == 0:
            break
        if "smartcaptcha" in " ".join(page_links):
            status("Yandex asked captcha, giving up")
            break
