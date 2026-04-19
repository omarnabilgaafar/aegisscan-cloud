from app.scanners.sql_injection_scanner import scan_sql_injection

def test_sql_scanner_returns_list():
    data = {"links": ["http://localhost:5000/page?id=1"], "html": ""}
    result = scan_sql_injection("http://localhost:5000/page?id=1", data)
    assert isinstance(result, list)