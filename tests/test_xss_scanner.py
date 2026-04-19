from app.scanners.xss_scanner import scan_xss

def test_xss_scanner_returns_list():
    data = {
        "links": ["http://localhost:5000/search?q=test"],
        "forms": [{"action": "/submit", "inputs": [{"name": "comment", "type": "text"}]}]
    }
    result = scan_xss("http://localhost:5000/search?q=test", data)
    assert isinstance(result, list)