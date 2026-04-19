from flask import Blueprint
from app.controllers.report_controller import (
    get_report_controller,
    download_report_pdf
)

report_bp = Blueprint("report", __name__)

@report_bp.route("/report/<int:scan_id>", methods=["GET"])
def view_report(scan_id):
    return get_report_controller(scan_id)

@report_bp.route("/report/<int:scan_id>/pdf", methods=["GET"])
def download_pdf(scan_id):
    return download_report_pdf(scan_id)