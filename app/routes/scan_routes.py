from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controllers.scan_controller import start_scan_controller
from app.database.db import get_connection
from app.services.demo_target_service import demo_target_examples, demo_target_details
from app.config import Config
import secrets

scan_bp = Blueprint("scan", __name__)

PLAN_LIMITS = {"Starter": 10, "Professional": 100, "Enterprise": None}
DEMO_MODE = Config.DEMO_MODE

@scan_bp.route("/", methods=["GET"])
def home():
    return render_template("index.html", demo_targets=demo_target_examples(), demo_target_details=demo_target_details(), demo_mode=DEMO_MODE)

@scan_bp.route("/scan", methods=["POST"])
def start_scan():
    usage = get_current_scan_usage()
    return start_scan_controller(request.form.get("target_url", "").strip(), usage)

@scan_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html", data=load_dashboard_data())

@scan_bp.route("/admin", methods=["GET"])
def admin_panel():
    if session.get("role") != "admin":
        return redirect(url_for("scan.dashboard"))
    return render_template("admin.html", data=load_admin_data())

@scan_bp.route('/workspace/api-key/rotate', methods=['POST'])
def rotate_api_key():
    if not session.get('organization_id') or not session.get('user_id'):
        return redirect(url_for('auth.login'))
    conn = get_connection()
    cur = conn.cursor()
    new_key = f"ags_{secrets.token_hex(16)}"
    cur.execute('INSERT INTO api_keys (user_id, organization_id, api_key, label) VALUES (?, ?, ?, ?)', (session['user_id'], session['organization_id'], new_key, 'Rotated API Key'))
    conn.commit()
    conn.close()
    flash('API key rotated successfully.', 'success')
    return redirect(url_for('scan.dashboard'))


def get_current_scan_usage():
    org_id = session.get('organization_id')
    conn = get_connection()
    cur = conn.cursor()
    if org_id:
        count = cur.execute('SELECT COUNT(*) AS count FROM scans WHERE organization_id = ?', (org_id,)).fetchone()['count']
    else:
        count = cur.execute('SELECT COUNT(*) AS count FROM scans').fetchone()['count']
    conn.close()
    return count


def _params_for_org(org_id):
    return ((org_id,), 'WHERE organization_id = ?', 'WHERE s.organization_id = ?') if org_id else (tuple(), '', '')


def load_dashboard_data():
    severity = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    org_id = session.get("organization_id")
    plan = session.get("plan", "Starter")
    plan_limit = PLAN_LIMITS.get(plan)
    try:
        conn = get_connection()
        cur = conn.cursor()
        params, scan_where, vuln_where = _params_for_org(org_id)

        total_scans = cur.execute(f"SELECT COUNT(*) AS count FROM scans {scan_where}", params).fetchone()["count"]
        total_findings = cur.execute(
            f"SELECT COUNT(*) AS count FROM vulnerabilities v JOIN scans s ON s.id=v.scan_id {vuln_where}", params
        ).fetchone()["count"]
        total_users = cur.execute("SELECT COUNT(*) AS count FROM users WHERE organization_id = ?", (org_id,)).fetchone()["count"] if org_id else cur.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]

        for row in cur.execute(
            f"SELECT v.severity, COUNT(*) AS count FROM vulnerabilities v JOIN scans s ON s.id=v.scan_id {vuln_where} GROUP BY v.severity",
            params
        ).fetchall():
            sev = (row["severity"] or "").strip().title()
            if sev in severity:
                severity[sev] = row["count"]

        recent_findings = [dict(row) for row in cur.execute(
            f"SELECT v.id, v.scan_id, v.vuln_type, v.severity, v.url, v.description, v.created_at FROM vulnerabilities v JOIN scans s ON s.id=v.scan_id {vuln_where} ORDER BY v.id DESC LIMIT 6",
            params).fetchall()]
        recent_scans = [dict(row) for row in cur.execute(
            f"SELECT id, target_url, total_findings, error_message, created_at FROM scans {scan_where} ORDER BY id DESC LIMIT 8",
            params).fetchall()]
        latest_scan_id = recent_scans[0]["id"] if recent_scans else None
        risk_score = severity["Critical"] * 10 + severity["High"] * 7 + severity["Medium"] * 4 + severity["Low"]
        api_row = cur.execute("SELECT api_key FROM api_keys WHERE organization_id = ? ORDER BY id DESC LIMIT 1", (org_id,)).fetchone() if org_id else None

        trend_rows = cur.execute(f"SELECT substr(created_at,1,10) AS day, COUNT(*) AS count FROM scans {scan_where} GROUP BY substr(created_at,1,10) ORDER BY day DESC LIMIT 7", params).fetchall()
        trend_rows = list(reversed([dict(row) for row in trend_rows]))
        top_targets = [dict(row) for row in cur.execute(f"SELECT target_url, COUNT(*) AS count FROM scans {scan_where} GROUP BY target_url ORDER BY count DESC, target_url ASC LIMIT 5", params).fetchall()]
        top_issue_types = [dict(row) for row in cur.execute(f"SELECT v.vuln_type, COUNT(*) AS count FROM vulnerabilities v JOIN scans s ON s.id=v.scan_id {vuln_where} GROUP BY v.vuln_type ORDER BY count DESC LIMIT 5", params).fetchall()]
        usage_percent = 0 if DEMO_MODE or not plan_limit else min(100, round((total_scans / plan_limit) * 100))
        conn.close()
        return {
            "total_scans": total_scans,
            "total_findings": total_findings,
            "total_users": total_users,
            "severity": severity,
            "severity_total": sum(severity.values()),
            "recent_findings": recent_findings,
            "recent_scans": recent_scans,
            "latest_scan_id": latest_scan_id,
            "risk_score": risk_score,
            "database_note": "Connected to live SQLite data with workspace-aware filtering.",
            "organization_name": session.get("organization_name", "Demo Workspace"),
            "workspace_plan": f"{plan} · Demo Mode" if DEMO_MODE else plan,
            "workspace_scans": total_scans,
            "scan_limit_label": "Unlimited (Demo Mode)" if DEMO_MODE else ("Unlimited" if plan_limit is None else str(plan_limit)),
            "usage_percent": usage_percent,
            "demo_mode": DEMO_MODE,
            "api_key_preview": (api_row["api_key"][:18] + "...") if api_row else "Not generated",
            "trend_labels": [row['day'] for row in trend_rows],
            "trend_values": [row['count'] for row in trend_rows],
            "top_targets": top_targets,
            "top_issue_types": top_issue_types,
        }
    except Exception as exc:
        return {
            "total_scans": 0, "total_findings": 0, "total_users": 1, "severity": severity, "severity_total": 0,
            "recent_findings": [], "recent_scans": [], "latest_scan_id": None, "risk_score": 0,
            "database_note": f"Fallback mode: {exc}", "organization_name": session.get("organization_name", "Demo Workspace"),
            "workspace_plan": f"{plan} · Demo Mode" if DEMO_MODE else plan, "workspace_scans": 0, "scan_limit_label": "Unlimited (Demo Mode)" if DEMO_MODE else ("Unlimited" if plan_limit is None else str(plan_limit)), "usage_percent": 0, "api_key_preview": "Unavailable", "demo_mode": DEMO_MODE,
            "trend_labels": [], "trend_values": [], "top_targets": [], "top_issue_types": []
        }


def load_admin_data():
    conn = get_connection()
    cur = conn.cursor()
    plan_distribution = {row['plan']: row['count'] for row in cur.execute("SELECT plan, COUNT(*) AS count FROM organizations GROUP BY plan").fetchall()}
    data = {
        "total_users": cur.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"],
        "total_organizations": cur.execute("SELECT COUNT(*) AS count FROM organizations").fetchone()["count"],
        "total_scans": cur.execute("SELECT COUNT(*) AS count FROM scans").fetchone()["count"],
        "total_api_keys": cur.execute("SELECT COUNT(*) AS count FROM api_keys").fetchone()["count"],
        "plan_distribution": plan_distribution,
        "organizations": [dict(row) for row in cur.execute("SELECT name, plan, created_at FROM organizations ORDER BY id DESC LIMIT 8").fetchall()],
        "users": [dict(row) for row in cur.execute("SELECT username, email, role, plan, created_at FROM users ORDER BY id DESC LIMIT 10").fetchall()],
    }
    conn.close()
    return data
