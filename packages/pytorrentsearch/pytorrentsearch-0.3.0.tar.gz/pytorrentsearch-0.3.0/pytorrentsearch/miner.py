import re

MAGNET_REGEXP = re.compile("magnet:\\?xt=[^\"']*")

nontorrent_blockwords = [
    "lumendatabase.org",
    "disney.com.br",
    "reddit.com",
    "facebook.com",
    "google.com",
    "youtube.com",
    "youtu.be",
    "wikipedia.org",
    "instagram.com",
    "ifunny.co",
    "9gag.com",
]


def is_common_nontorrent_site(url: str):
    for nontorrent_blockword in nontorrent_blockwords:
        if url.find(nontorrent_blockword) > 0:
            return True
    return False


def mine_magnet_links(url: str):
    from urllib.parse import unquote

    from pytorrentsearch.utils import get_url_content, status

    if is_common_nontorrent_site(url):
        status(f"[crawler/ENONTORRNET] {url}")
        return []
    status(f"[crawler/fetch] {url}")
    content = get_url_content(url)
    ret = []
    for occurence in MAGNET_REGEXP.findall(content):
        link = unquote(occurence)
        link = link.replace("&#038;", "&")
        link = link.replace("&amp;", "&")
        ret.append(link)
    return ret


def parse_magnet_link(url: str):
    from urllib.parse import parse_qs, urlparse

    query = urlparse(url).query
    query_params = parse_qs(query)
    info_hash = query_params["xt"][0].replace("urn:", "").replace("btih:", "")
    name = "< NO NAME >"
    if query_params.get("dn") is not None:
        name = query_params["dn"][0]
    trackers = []
    if query_params.get("tr") is not None:
        trackers = query_params["tr"]
    return dict(info_hash=info_hash, name=name, trackers=trackers)


def prettyprint_magnet(magnet: str):
    parsed = parse_magnet_link(magnet)
    len_trackers = len(parsed["trackers"])
    print(
        f"{parsed['name']}\nTrackers: {str(len_trackers).rjust(3)} InfoHash: {parsed['info_hash']}\n{magnet}\n"  # noqa: E501
    )
