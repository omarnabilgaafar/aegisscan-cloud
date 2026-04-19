from urllib.parse import urlparse

DEMO_TARGETS = {
    "demo.aegisscan.local": [
        {"type": "Potential Stored/Reflected XSS Surface", "severity": "High", "url": "https://demo.aegisscan.local/portal/search?q=<script>", "description": "Search input appears reflected in the portal response without sufficient output encoding, creating a realistic XSS testing surface."},
        {"type": "Missing CSRF Protection", "severity": "Medium", "url": "https://demo.aegisscan.local/portal/profile", "description": "State-changing portal forms do not expose an anti-CSRF token, so authenticated actions could be forged from another site."},
        {"type": "Missing Security Header", "severity": "Low", "url": "https://demo.aegisscan.local/portal", "description": "The response is missing a Content-Security-Policy header, reducing browser-side protection against script injection."},
        {"type": "Potential Directory Traversal Surface", "severity": "High", "url": "https://demo.aegisscan.local/portal/download?file=../../etc/passwd", "description": "The download handler accepts user-controlled file names and appears to lack strict normalization or allowlisting."},
    ],
    "shop.aegis-demo.local": [
        {"type": "Potential SQL Injection Surface", "severity": "Critical", "url": "https://shop.aegis-demo.local/products?id=10", "description": "Product identifiers are consumed in a query-like flow, suggesting that unsafe concatenation could expose backend data."},
        {"type": "Potential Stored/Reflected XSS Surface", "severity": "High", "url": "https://shop.aegis-demo.local/reviews", "description": "Review content is rendered in a customer-facing page and looks insufficiently sanitized before output."},
        {"type": "Missing CSRF Protection", "severity": "Medium", "url": "https://shop.aegis-demo.local/cart/checkout", "description": "Checkout and profile forms did not show anti-CSRF controls in the simulated storefront workflow."},
        {"type": "Missing Security Header", "severity": "Low", "url": "https://shop.aegis-demo.local/", "description": "The storefront response is missing X-Frame-Options, which can increase clickjacking exposure."},
    ],
    "files.aegis-demo.local": [
        {"type": "Potential Directory Traversal Surface", "severity": "Critical", "url": "https://files.aegis-demo.local/download?path=../../secrets.env", "description": "The file download workflow accepts relative path segments and resembles a classic traversal-sensitive endpoint."},
        {"type": "Missing Security Header", "severity": "Low", "url": "https://files.aegis-demo.local/", "description": "The file service lacks X-Content-Type-Options, increasing browser MIME-sniffing risk."},
        {"type": "Possible Database Error Disclosure", "severity": "Medium", "url": "https://files.aegis-demo.local/archive?folder='", "description": "An error-like response pattern suggests backend exceptions may leak implementation details during malformed requests."},
    ],
    "api.aegis-demo.local": [
        {"type": "Potential SQL Injection Surface", "severity": "High", "url": "https://api.aegis-demo.local/v1/users?id=1", "description": "Numeric identifiers appear in a query-like API surface that should be treated as parameterization-sensitive."},
        {"type": "Missing Security Header", "severity": "Low", "url": "https://api.aegis-demo.local/v1", "description": "The API response is missing a strict transport security policy and additional defensive headers."},
        {"type": "Possible Database Error Disclosure", "severity": "Medium", "url": "https://api.aegis-demo.local/v1/search?q='", "description": "Malformed request handling appears to expose structured error details that could help attackers map backend behavior."},
    ],
    "admin.aegis-demo.local": [
        {"type": "Potential Stored/Reflected XSS Surface", "severity": "High", "url": "https://admin.aegis-demo.local/users?search=<svg/onload=alert(1)>", "description": "Administrative search and filtering output appears to reflect user input in a privileged interface."},
        {"type": "Missing CSRF Protection", "severity": "High", "url": "https://admin.aegis-demo.local/settings", "description": "Administrator-facing update forms do not expose anti-CSRF tokens in the simulated management workflow."},
        {"type": "Missing Security Header", "severity": "Low", "url": "https://admin.aegis-demo.local/", "description": "The admin console is missing a Content-Security-Policy header, reducing browser hardening for a privileged surface."},
        {"type": "Possible Database Error Disclosure", "severity": "Medium", "url": "https://admin.aegis-demo.local/logs?filter='", "description": "Malformed filter values trigger error-like output that may disclose internal structures or stack traces."},
    ],
}

TARGET_META = {
    "https://demo.aegisscan.local/portal": {"name": "Customer Portal", "summary": "Portal-style target with XSS, CSRF, and traversal surfaces.", "risk": "High"},
    "https://shop.aegis-demo.local": {"name": "E-Commerce Shop", "summary": "Storefront demo with critical injection risk and weaker browser controls.", "risk": "Critical"},
    "https://files.aegis-demo.local": {"name": "File Service", "summary": "Download-heavy property with traversal-sensitive endpoints and disclosure issues.", "risk": "Critical"},
    "https://api.aegis-demo.local/v1": {"name": "Public API", "summary": "API surface with query validation concerns and response hardening gaps.", "risk": "High"},
    "https://admin.aegis-demo.local": {"name": "Admin Console", "summary": "Privileged interface with XSS/CSRF concerns and elevated business impact.", "risk": "Critical"},
}


def _normalized_host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def is_demo_target_url(url: str) -> bool:
    host = _normalized_host(url)
    return host in DEMO_TARGETS


def get_demo_findings(url: str) -> list[dict]:
    host = _normalized_host(url)
    findings = DEMO_TARGETS.get(host, [])
    if not findings:
        return []
    return [dict(item) for item in findings]


def demo_target_examples() -> list[str]:
    return list(TARGET_META.keys())


def demo_target_details() -> list[dict]:
    details = []
    for url in demo_target_examples():
        meta = TARGET_META.get(url, {})
        details.append({
            "url": url,
            "name": meta.get("name", urlparse(url).hostname or url),
            "summary": meta.get("summary", "Authorized demo target."),
            "risk": meta.get("risk", "Moderate"),
        })
    return details
