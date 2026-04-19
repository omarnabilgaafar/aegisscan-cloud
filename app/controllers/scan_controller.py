from flask import render_template, request, session
from app.config import Config
from app.services.validation_service import validate_target_url
from app.services.scanner_service import run_full_scan
from app.services.report_service import save_scan_result

PLAN_LIMITS = {"Starter": 10, "Professional": 100, "Enterprise": None}
DEMO_MODE = Config.DEMO_MODE


def start_scan_controller(target_url: str, current_usage: int = 0):
    csrf_token = request.form.get("csrf_token", "").strip()

    if not csrf_token:
        return render_template("scan_result.html", result={
            "target": target_url,
            "total": 0,
            "findings": [],
            "error": "Missing CSRF token."
        })

    plan = session.get('plan', 'Starter')
    limit = PLAN_LIMITS.get(plan)
    if limit is not None and current_usage >= limit and not DEMO_MODE:
        return render_template("scan_result.html", result={
            "target": target_url,
            "total": 0,
            "findings": [],
            "error": f"Scan limit reached for the {plan} plan. Upgrade your workspace to continue scanning."
        })

    is_valid, message = validate_target_url(target_url)

    if not is_valid:
        return render_template("scan_result.html", result={
            "target": target_url,
            "total": 0,
            "findings": [],
            "error": message
        })

    result = run_full_scan(target_url)
    scan_id = save_scan_result(result)
    result["scan_id"] = scan_id

    return render_template("scan_result.html", result=result)
