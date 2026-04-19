from app.main import app
from app.database.schema import init_db
from app.services.scanner_service import run_full_scan
from app.services.report_service import save_scan_result

TARGETS = [
    "https://admin.aegis-demo.local",
    "https://api.aegis-demo.local/v1",
    "https://files.aegis-demo.local",
    "https://shop.aegis-demo.local",
    "https://demo.aegisscan.local/portal",
]

if __name__ == "__main__":
    with app.app_context():
        init_db()
        from flask import session
        with app.test_request_context('/'):
            session['organization_id'] = 1
            session['plan'] = 'Professional'
            session['organization_name'] = 'Demo Workspace'
            for target in TARGETS:
                result = run_full_scan(target)
                scan_id = save_scan_result(result)
                print(f"Saved scan #{scan_id}: {target} ({result['total']} findings)")
