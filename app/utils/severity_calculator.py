def calculate_severity(vuln_type: str):
    mapping = {
        "Missing Security Header": "Medium",
        "Potential Reflected XSS Surface": "Medium",
        "Potential Stored/Reflected XSS Surface": "Medium",
        "Potential SQL Injection Surface": "Medium",
        "Possible Database Error Disclosure": "High",
        "Potential CSRF Risk": "Medium",
        "Potential Directory Traversal Surface": "Medium"
    }
    return mapping.get(vuln_type, "Low")