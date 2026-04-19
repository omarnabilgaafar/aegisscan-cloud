from urllib.parse import urlparse, parse_qs

SUSPICIOUS_PARAM_NAMES = {"file", "path", "filepath", "template", "folder", "document", "download"}

def scan_directory_traversal(target_url: str, crawl_data: dict):
    """
    Defensive / non-invasive educational check:
    - flags suspicious parameter names that often map to filesystem access
    """
    findings = []

    links = [target_url] + crawl_data.get("links", [])
    seen = set()

    for link in links:
        if link in seen:
            continue
        seen.add(link)

        parsed = urlparse(link)
        params = parse_qs(parsed.query, keep_blank_values=True)

        risky = [name for name in params.keys() if name.lower() in SUSPICIOUS_PARAM_NAMES]

        if risky:
            findings.append({
                "type": "Potential Directory Traversal Surface",
                "severity": "Medium",
                "url": link,
                "description": f"Suspicious file/path-related parameters found: {', '.join(risky)}. Ensure canonicalization and strict allowlists."
            })

    return findings