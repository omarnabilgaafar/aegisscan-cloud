import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from app.config import Config

def fetch_page(url: str):
    response = requests.get(
        url,
        timeout=Config.REQUEST_TIMEOUT,
        headers={"User-Agent": "SmartWebScanner/1.0"}
    )
    response.raise_for_status()
    return response

def extract_links_and_forms(base_url: str):
    response = fetch_page(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    parsed_base = urlparse(base_url)
    base_host = parsed_base.hostname

    links = []
    forms = []

    for a_tag in soup.find_all("a", href=True):
        href = urljoin(base_url, a_tag["href"])
        parsed_href = urlparse(href)

        if parsed_href.scheme in ("http", "https") and parsed_href.hostname == base_host:
            links.append(href)

    for form in soup.find_all("form"):
        method = form.get("method", "get").lower()
        action = form.get("action", "")
        action_url = urljoin(base_url, action)

        inputs = []
        for input_tag in form.find_all(["input", "textarea", "select"]):
            inputs.append({
                "name": input_tag.get("name"),
                "type": input_tag.get("type", "text")
            })

        forms.append({
            "method": method,
            "action": action_url,
            "inputs": inputs
        })

    unique_links = list(dict.fromkeys(links))[:Config.MAX_LINKS_TO_SCAN]

    return {
        "base_url": base_url,
        "html": response.text,
        "links": unique_links,
        "forms": forms,
        "params": parse_qs(urlparse(base_url).query)
    }