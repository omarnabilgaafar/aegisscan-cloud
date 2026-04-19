from collections import Counter

SEVERITY_WEIGHTS = {"Low": 1, "Medium": 4, "High": 7, "Critical": 10}

RECOMMENDATION_MAP = {
    "Potential Reflected XSS Surface": "Apply context-aware output encoding, validate all user-controlled parameters, and deploy a restrictive Content-Security-Policy.",
    "Potential Stored/Reflected XSS Surface": "Sanitize and encode form input on output, validate rich-text fields, and separate trusted from untrusted HTML.",
    "Potential SQL Injection Surface": "Use parameterized queries only, reject unsafe input patterns early, and avoid building SQL statements dynamically.",
    "Possible Database Error Disclosure": "Disable verbose database errors in production and replace them with generic user-safe messages while logging full details server-side.",
    "Missing CSRF Protection": "Add anti-CSRF tokens to state-changing forms and validate them server-side for every authenticated request.",
    "Potential Directory Traversal Surface": "Normalize file paths, allowlist accessible resources, and reject path segments such as ../ or encoded traversal payloads.",
    "Missing Security Header": "Set the missing security header at the reverse-proxy or application layer and verify it on every sensitive response.",
}

BUSINESS_IMPACT_MAP = {
    "Potential Reflected XSS Surface": "Client-side session theft or malicious script execution in a victim browser.",
    "Potential Stored/Reflected XSS Surface": "Persistent malicious content could affect multiple users or administrators.",
    "Potential SQL Injection Surface": "Unauthorized data access, modification, or authentication bypass if input reaches the database unsafely.",
    "Possible Database Error Disclosure": "Attackers gain insight into backend technologies and query structure, reducing effort for deeper exploitation.",
    "Missing CSRF Protection": "Authenticated users may be tricked into performing unintended state-changing actions.",
    "Potential Directory Traversal Surface": "Sensitive files or internal application data may become accessible outside intended directories.",
    "Missing Security Header": "Browsers lose a layer of protection against clickjacking, MIME confusion, or script injection abuse.",
}


def normalize_severity(value: str) -> str:
    text = (value or '').strip().title()
    return text if text in SEVERITY_WEIGHTS else 'Low'


def enrich_finding(finding: dict) -> dict:
    item = dict(finding)
    vuln_type = item.get('type') or item.get('vuln_type') or 'Security Finding'
    severity = normalize_severity(item.get('severity'))
    item['severity'] = severity
    item['recommendation'] = RECOMMENDATION_MAP.get(vuln_type, 'Review the affected surface, confirm exploitability in a safe test environment, and remediate at the source rather than filtering symptoms only.')
    item['business_impact'] = BUSINESS_IMPACT_MAP.get(vuln_type, 'This weakness increases the attack surface and should be reviewed during remediation planning.')
    item['confidence'] = 'Medium' if severity in {'Low', 'Medium'} else 'High'
    return item


def enrich_findings(findings: list[dict]) -> list[dict]:
    return [enrich_finding(item) for item in findings]


def compute_severity_count(findings: list[dict]) -> dict:
    counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    for item in findings:
        counts[normalize_severity(item.get('severity'))] += 1
    return counts


def compute_risk_score(findings: list[dict]) -> tuple[int, str]:
    score = sum(SEVERITY_WEIGHTS[normalize_severity(item.get('severity'))] for item in findings)
    if score >= 35:
        band = 'Critical'
    elif score >= 20:
        band = 'High'
    elif score >= 8:
        band = 'Medium'
    else:
        band = 'Low'
    return score, band


def summarize_findings(findings: list[dict]) -> dict:
    enriched = enrich_findings(findings)
    severity = compute_severity_count(enriched)
    score, band = compute_risk_score(enriched)
    top_types = Counter((item.get('type') or item.get('vuln_type') or 'Unknown') for item in enriched).most_common(5)
    return {
        'findings': enriched,
        'severity_count': severity,
        'risk_score': score,
        'risk_band': band,
        'top_types': top_types,
    }
