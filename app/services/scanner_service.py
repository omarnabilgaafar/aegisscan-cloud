from app.services.crawler_service import extract_links_and_forms
from app.services.demo_target_service import is_demo_target_url, get_demo_findings
from app.scanners.xss_scanner import scan_xss
from app.scanners.sql_injection_scanner import scan_sql_injection
from app.scanners.csrf_scanner import scan_csrf
from app.scanners.directory_traversal_scanner import scan_directory_traversal
from app.scanners.security_headers_scanner import scan_security_headers
from app.services.insight_service import summarize_findings


def _format_summary(target_url: str, findings: list[dict], error: str | None = None):
    summary = summarize_findings(findings)
    return {
        "target": target_url,
        "total": len(summary["findings"]),
        "findings": summary["findings"],
        "severity_count": summary["severity_count"],
        "risk_score": summary["risk_score"],
        "risk_band": summary["risk_band"],
        "top_types": summary["top_types"],
        "error": error,
    }


def run_full_scan(target_url: str):
    if is_demo_target_url(target_url):
        return _format_summary(target_url, get_demo_findings(target_url), None)

    findings = []
    try:
        crawl_data = extract_links_and_forms(target_url)
        findings.extend(scan_security_headers(target_url))
        findings.extend(scan_xss(target_url, crawl_data))
        findings.extend(scan_sql_injection(target_url, crawl_data))
        findings.extend(scan_csrf(target_url, crawl_data))
        findings.extend(scan_directory_traversal(target_url, crawl_data))
        return _format_summary(target_url, findings, None)
    except Exception as exc:
        return _format_summary(target_url, findings, f"Scan completed with limited coverage: {exc}")
