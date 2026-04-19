from urllib.parse import urlparse

def get_host(url: str):
    parsed = urlparse(url)
    return parsed.hostname