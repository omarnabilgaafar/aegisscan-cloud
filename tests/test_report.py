from app.services.report_service import save_scan_result

def test_save_scan_result_returns_id():
    result = {
        "target": "http://localhost:5000",
        "total": 1,
        "findings": [
            {
                "type": "Missing Security Header",
                "severity": "Medium",
                "url": "http://localhost:5000",
                "description": "Missing header: X-Frame-Options"
            }
        ],
        "error": None
    }
    scan_id = save_scan_result(result)
    assert isinstance(scan_id, int)