from urllib.parse import urlparse, parse_qs

def scan_xss(target_url: str, crawl_data: dict):
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
                "type": "Potential Reflected XSS Surface",
                "severity": "Medium",
                "url": link,
                "description": "URL contains user-controlled query parameters. Verify output encoding and context-aware escaping on server-side rendering."
            })

    for form in crawl_data.get("forms", []):
        action_url = form.get("action") or target_url

        # تجاهل فورم الفحص الداخلي نفسه
        if action_url.rstrip("/") == f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}/scan":
            continue

        risky_inputs = []
        for field in form.get("inputs", []):
            field_type = (field.get("type") or "text").lower()
            if field_type in ("text", "search", "email", "url", "textarea", "hidden"):
                risky_inputs.append(field.get("name") or "(unnamed field)")

        if risky_inputs:
            findings.append({
                "type": "Potential Stored/Reflected XSS Surface",
                "severity": "Medium",
                "url": action_url,
                "description": f"Form accepts user input fields that should be validated and safely encoded before rendering: {', '.join(risky_inputs)}."
            })

    return findings