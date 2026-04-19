from app.database.db import get_connection
from flask import session
from app.services.insight_service import summarize_findings
import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def save_scan_result(result: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scans (target_url, total_findings, error_message, user_id, organization_id) VALUES (?, ?, ?, ?, ?)",
        (result["target"], result["total"], result.get("error"), session.get("user_id"), session.get("organization_id"))
    )
    scan_id = cursor.lastrowid

    for finding in result["findings"]:
        cursor.execute(
            """
            INSERT INTO vulnerabilities (scan_id, vuln_type, severity, url, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                scan_id,
                finding.get("type") or finding.get("vuln_type"),
                finding.get("severity"),
                finding.get("url"),
                finding.get("description"),
            ),
        )

    conn.commit()
    conn.close()
    return scan_id



def get_scan_by_id(scan_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None



def get_vulnerabilities_by_scan_id(scan_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vulnerabilities WHERE scan_id = ? ORDER BY id DESC", (scan_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]



def build_report_context(scan_id: int):
    scan = get_scan_by_id(scan_id)
    findings = get_vulnerabilities_by_scan_id(scan_id)
    if not scan:
        return None
    summary = summarize_findings(findings)
    return {
        "report": scan,
        "findings": summary["findings"],
        "severity_count": summary["severity_count"],
        "risk_score": summary["risk_score"],
        "risk_band": summary["risk_band"],
        "top_types": summary["top_types"],
    }



def _reports_dir():
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir



def _severity_color(severity: str):
    mapping = {
        "Critical": colors.HexColor("#dc2626"),
        "High": colors.HexColor("#ea580c"),
        "Medium": colors.HexColor("#d97706"),
        "Low": colors.HexColor("#64748b"),
    }
    return mapping.get(severity, colors.HexColor("#334155"))



def _safe_text(value):
    text = str(value or "-")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )



def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Brand",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#475569"),
            spaceAfter=4,
            alignment=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeroTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
            spaceBefore=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Label",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748b"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Value",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0f172a"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.4,
            leading=10.8,
            textColor=colors.HexColor("#1f2937"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.4,
            leading=10.8,
            textColor=colors.HexColor("#111827"),
        )
    )
    return styles



def _build_pdf_story(context: dict):
    report = context["report"]
    findings = context["findings"]
    severity_count = context["severity_count"]
    risk_score = context["risk_score"]
    risk_band = context["risk_band"]
    top_types = context["top_types"]

    styles = _styles()
    story = []

    story.append(Paragraph("AEGISSCAN CLOUD", styles["Brand"]))
    story.append(Paragraph("Executive Security Assessment Report", styles["HeroTitle"]))
    story.append(
        Paragraph(
            "A polished report for portfolio demos, recruiter review, and remediation planning. Built to make the risk story obvious at a glance.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 10))

    kpi_data = [
        [
            Paragraph("TARGET", styles["Label"]),
            Paragraph("TOTAL FINDINGS", styles["Label"]),
            Paragraph("RISK SCORE", styles["Label"]),
        ],
        [
            Paragraph(_safe_text(report.get("target_url")), styles["Value"]),
            Paragraph(_safe_text(report.get("total_findings")), styles["Value"]),
            Paragraph(f"{risk_score} / {_safe_text(risk_band)}", styles["Value"]),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[76 * mm, 36 * mm, 50 * mm])
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#dbe3ef")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    left_summary = [
        Paragraph("1. Executive Summary", styles["SectionHeading"]),
        Paragraph(
            "This assessment detected a mix of exploitable flaws and weaker defensive controls. High-priority findings should be remediated first, especially any issue that could lead to account compromise, data exposure, or application takeover.",
            styles["Body"],
        ),
    ]

    risk_box = Table(
        [
            [Paragraph("Overall Risk", styles["SectionHeading"])],
            [Paragraph(str(risk_score), ParagraphStyle(name="RiskScore", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=colors.HexColor("#111827")))],
            [Paragraph(_safe_text(risk_band.upper()), ParagraphStyle(name="RiskBand", fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=_severity_color(risk_band)))],
            [Paragraph("Risk score is weighted by severity and intended to make prioritization obvious for engineering teams.", styles["BodySmall"])],
        ],
        colWidths=[58 * mm],
    )
    risk_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#dbe3ef")),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    summary_table = Table([[left_summary, risk_box]], colWidths=[112 * mm, 58 * mm])
    summary_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Severity Snapshot", styles["SectionHeading"]))
    sev_data = [
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        [str(severity_count["Critical"]), str(severity_count["High"]), str(severity_count["Medium"]), str(severity_count["Low"])],
    ]
    sev_table = Table(sev_data, colWidths=[42 * mm, 42 * mm, 42 * mm, 42 * mm])
    sev_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4ff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 11),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#dbe3ef")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(sev_table)
    story.append(Spacer(1, 12))

    top_types_list = "<br/>".join([f"- {_safe_text(name)} - {count}" for name, count in top_types]) or "- No repeated categories detected"
    next_steps = "<br/>".join([
        "- Fix critical and high findings first.",
        "- Retest all affected endpoints after remediation.",
        "- Harden input validation and security headers.",
        "- Track closure in the engineering backlog.",
    ])
    boxes = Table(
        [
            [
                Paragraph("3. Top Finding Categories", styles["SectionHeading"]),
                Paragraph("4. Recommended Next Steps", styles["SectionHeading"]),
            ],
            [
                Paragraph(top_types_list, styles["Body"]),
                Paragraph(next_steps, styles["Body"]),
            ],
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    boxes.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#dbe3ef")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(boxes)
    story.append(Spacer(1, 14))

    story.append(Paragraph("5. Findings & Remediation", styles["SectionHeading"]))
    findings_rows = [[
        Paragraph("#", styles["TableCellBold"]),
        Paragraph("FINDING", styles["TableCellBold"]),
        Paragraph("SEVERITY", styles["TableCellBold"]),
        Paragraph("URL", styles["TableCellBold"]),
        Paragraph("BUSINESS IMPACT", styles["TableCellBold"]),
        Paragraph("RECOMMENDATION", styles["TableCellBold"]),
    ]]
    for idx, item in enumerate(findings, 1):
        findings_rows.append([
            Paragraph(str(idx), styles["TableCell"]),
            Paragraph(f"<b>{_safe_text(item.get('vuln_type') or item.get('type'))}</b><br/>{_safe_text(item.get('description'))}", styles["TableCell"]),
            Paragraph(_safe_text(item.get("severity")), ParagraphStyle(name=f"Sev{idx}", parent=styles["TableCellBold"], textColor=_severity_color(item.get("severity")))),
            Paragraph(_safe_text(item.get("url")), styles["TableCell"]),
            Paragraph(_safe_text(item.get("business_impact")), styles["TableCell"]),
            Paragraph(_safe_text(item.get("recommendation")), styles["TableCell"]),
        ])
    findings_table = Table(
        findings_rows,
        repeatRows=1,
        colWidths=[8 * mm, 40 * mm, 22 * mm, 40 * mm, 40 * mm, 40 * mm],
    )
    findings_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4ff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#dbe3ef")),
                ("INNERGRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#e5e7eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(findings_table)
    return story



def _page_canvas(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(doc.leftMargin, 18 * mm, A4[0] - doc.rightMargin, 18 * mm)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#64748b"))
    canvas_obj.drawString(doc.leftMargin, 12 * mm, "Generated by AegisScan Cloud - Confidential - For authorized security testing only.")
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, 12 * mm, f"Page {canvas_obj.getPageNumber()}")
    canvas_obj.restoreState()



def generate_pdf_report(scan, findings, severity_count=None):
    summary = summarize_findings(findings)
    output_path = os.path.join(_reports_dir(), f"report_{scan['id']}.pdf")
    context = {
        "report": scan,
        "findings": summary["findings"],
        "severity_count": severity_count or summary["severity_count"],
        "risk_score": summary["risk_score"],
        "risk_band": summary["risk_band"],
        "top_types": summary["top_types"],
    }

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=16 * mm,
        bottomMargin=22 * mm,
        title=f"AegisScan Cloud Report #{scan['id']}",
        author="AegisScan Cloud",
    )
    story = _build_pdf_story(context)
    doc.build(story, onFirstPage=_page_canvas, onLaterPages=_page_canvas)
    return output_path
