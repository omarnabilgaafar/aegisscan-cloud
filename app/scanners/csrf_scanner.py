from urllib.parse import urlparse

def scan_csrf(target_url: str, crawl_data: dict):
    findings = []

    token_like_names = {"csrf", "csrf_token", "_token", "xsrf_token", "authenticity_token"}
    parsed_target = urlparse(target_url)
    internal_scan_url = f"{parsed_target.scheme}://{parsed_target.netloc}/scan"

    for form in crawl_data.get("forms", []):
        method = (form.get("method") or "get").lower()
        action_url = form.get("action") or target_url

        if method != "post":
            continue

        if action_url.rstrip("/") == internal_scan_url.rstrip("/"):
            continue

        field_names = {
            (field.get("name") or "").lower()
            for field in form.get("inputs", [])
            if field.get("name")
        }

        has_token = any(name in field_names for name in token_like_names)

        if not has_token:
            findings.append({
                "type": "Potential CSRF Risk",
                "severity": "Medium",
                "url": action_url,
                "description": "POST form does not appear to contain a recognizable CSRF token field."
            })

    return findings