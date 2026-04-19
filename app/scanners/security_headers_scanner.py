import requests
from app.config import Config

def scan_security_headers(target_url: str):
    findings = []
    response = requests.get(
        target_url,
        timeout=Config.REQUEST_TIMEOUT,
        headers={"User-Agent": "SmartWebScanner/1.0"}
    )

    required_headers = {
        "Content-Security-Policy": "High",
        "X-Frame-Options": "Medium",
        "X-Content-Type-Options": "Medium",
        "Strict-Transport-Security": "Medium",
        "Referrer-Policy": "Low"
    }

    for header_name, severity in required_headers.items():
        if header_name not in response.headers:
            findings.append({
                "type": "Missing Security Header",
                "severity": severity,
                "url": target_url,
                "description": f"Missing header: {header_name}"
            })

    return findings