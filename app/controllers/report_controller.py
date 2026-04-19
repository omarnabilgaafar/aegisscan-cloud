from flask import render_template, send_file
from app.services.report_service import build_report_context, generate_pdf_report


def get_report_controller(scan_id: int):
    context = build_report_context(scan_id)
    if not context:
        return render_template("report.html", report=None, findings=[])
    return render_template("report.html", **context)


def download_report_pdf(scan_id: int):
    context = build_report_context(scan_id)
    if not context:
        return render_template("report.html", report=None, findings=[])

    pdf_path = generate_pdf_report(context['report'], context['findings'], context['severity_count'])
    return send_file(pdf_path, as_attachment=True)
