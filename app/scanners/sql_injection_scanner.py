from urllib.parse import urlparse, parse_qs

SQLI_SUSPICIOUS_ERROR_PATTERNS = [
    "sql syntax",
    "mysql",
    "postgresql",
    "sqlite",
    "quoted string not properly terminated",
    "unclosed quotation mark"
]

def scan_sql_injection(target_url: str, crawl_data: dict):
    """
    Defensive / non-invasive educational check:
    - flags pages with query parameters as higher-risk input points
    - flags pages whose already-fetched HTML contains obvious DB error strings
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

        if params:
            findings.append({
                "type": "Potential SQL Injection Surface",
                "severity": "Medium",
                "url": link,
                "description": "URL contains query parameters that should be reviewed for proper server-side validation and parameterized queries."
            })

    html = (crawl_data.get("html") or "").lower()
    for pattern in SQLI_SUSPICIOUS_ERROR_PATTERNS:
        if pattern in html:
            findings.append({
                "type": "Possible Database Error Disclosure",
                "severity": "High",
                "url": target_url,
                "description": f"Response appears to expose a database-related error message pattern: '{pattern}'."
            })
            break

    return findings