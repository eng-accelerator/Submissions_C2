from fastapi import APIRouter, HTTPException, Response
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
import io

router = APIRouter()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Heading1Center", parent=styles["Heading1"], alignment=1))
styles.add(ParagraphStyle(name="Small", fontSize=8, leading=10, textColor=colors.grey))


def load_local_image(path):
    """Load image and scale keeping both width and height constraints."""
    path = path.replace("\\", "/")
    if not os.path.exists(path):
        return None

    try:
        img = Image(path)

        max_w = 15 * cm
        max_h = 18 * cm
        w, h = img.drawWidth, img.drawHeight

        scale = min(max_w / w, max_h / h, 1.0)
        img.drawWidth = w * scale
        img.drawHeight = h * scale
        img.hAlign = "LEFT"

        return img
    except Exception:
        return None


def build_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    project = data["project"]
    screens = data["screens"]
    analysis = data["analysis"][0]["result_json"]["screens"]

    # ---------- COVER PAGE ----------
    story.append(Paragraph(project["name"], styles["Heading1Center"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Design Type:</b> {project['design_type']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Persona:</b> {project['persona']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Goals:</b> {project['goals']}", styles["Normal"]))
    story.append(Spacer(1, 36))
    story.append(Paragraph("Generated UX, Visual & Accessibility Review Report", styles["Italic"]))
    story.append(PageBreak())

    # ---------- PER SCREEN ----------
    for screen in screens:
        path = screen["file_path"]
        result = analysis.get(path, {})

        story.append(Paragraph(screen["original_name"], styles["Heading2"]))
        story.append(Spacer(1, 6))

        img = load_local_image(screen["file_path"])
        if img:
            story.append(img)
            story.append(Spacer(1, 12))

        # ----- VISUAL -----
        visual = result.get("visual")
        if visual:
            story.append(Paragraph("Visual Design Review", styles["Heading3"]))

            strengths = visual.get("strengths", [])
            if strengths:
                story.append(Paragraph("Strengths:", styles["Heading4"]))
                for s in strengths:
                    story.append(Paragraph(f"• {s}", styles["Normal"]))

            issues = visual.get("issues", [])
            if issues:
                story.append(Spacer(1, 6))
                story.append(Paragraph("Issues:", styles["Heading4"]))
                for issue in issues:
                    story.append(Paragraph(
                        f"<b>Description:</b> {issue.get('description', '')}<br/>"
                        f"<b>Impact:</b> {issue.get('impact', '')} | <b>Effort:</b> {issue.get('effort', '')}<br/>"
                        f"<b>Recommendation:</b> {issue.get('recommendation', '')}",
                        styles["Normal"]
                    ))
                    story.append(Spacer(1, 4))

            meta = visual.get("_meta", {})
            story.append(Paragraph(
                f"<i>Model:</i> {meta.get('model', '')} | "
                f"<i>Tokens:</i> {meta.get('tokens', 0)} | "
                f"<i>Cost:</i> ${meta.get('cost_usd', 0):.4f} | "
                f"<i>Batch Mode:</i> {meta.get('batchMode', '')}",
                styles["Small"]
            ))
            story.append(Spacer(1, 12))

        # ----- UX -----
        ux = result.get("ux")
        if ux:
            story.append(Paragraph("UX Heuristic Review", styles["Heading3"]))

            problems = ux.get("usability_problems", [])
            if problems:
                story.append(Paragraph("Usability Problems:", styles["Heading4"]))
                for p in problems:
                    story.append(Paragraph(
                        f"<b>Description:</b> {p.get('description', '')}<br/>"
                        f"<b>Impact:</b> {p.get('impact', '')} | <b>Effort:</b> {p.get('effort', '')}<br/>"
                        f"<b>Improvement:</b> {p.get('improvement', '')}",
                        styles["Normal"]
                    ))
                    story.append(Spacer(1, 4))

            confusing = ux.get("confusing_elements", [])
            if confusing:
                story.append(Spacer(1, 6))
                story.append(Paragraph("Confusing Elements:", styles["Heading4"]))
                for c in confusing:
                    story.append(Paragraph(f"• {c}", styles["Normal"]))

            improvements = ux.get("improvements", [])
            if improvements:
                story.append(Spacer(1, 6))
                story.append(Paragraph("Recommended Improvements:", styles["Heading4"]))
                for x in improvements:
                    story.append(Paragraph(f"• {x}", styles["Normal"]))

            meta = ux.get("_meta", {})
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"<i>Model:</i> {meta.get('model', '')} | "
                f"<i>Tokens:</i> {meta.get('tokens', 0)} | "
                f"<i>Cost:</i> ${meta.get('cost_usd', 0):.4f} | "
                f"<i>Batch Mode:</i> {meta.get('batchMode', '')}",
                styles["Small"]
            ))
            story.append(Spacer(1, 12))
                # ----- PERSONA INSIGHTS -----
        # ---- Persona -----
        persona = result.get("persona")
        if persona:
            story.append(Paragraph("Persona Alignment Review", styles["Heading3"]))

            # Scores
            trust_score = persona.get("trust_score")
            clarity_score = persona.get("clarity_score")
            if trust_score or clarity_score:
                story.append(Paragraph(
                    f"Trust Score: <b>{trust_score}</b> / 100 &nbsp;&nbsp; | &nbsp;&nbsp; "
                    f"Clarity Score: <b>{clarity_score}</b> / 100",
                    styles["Normal"]
                ))
                story.append(Spacer(1, 6))

            # Confusion Points
            confusion = persona.get("confusion_points", [])
            if confusion:
                story.append(Paragraph("Confusion Points:", styles["Heading4"]))
                for c in confusion:
                    story.append(Paragraph(f"• {c}", styles["Normal"]))

            # Recommendations
            recs = persona.get("recommendations", [])
            if recs:
                story.append(Spacer(1, 6))
                story.append(Paragraph("Recommendations:", styles["Heading4"]))
                for r in recs:
                    story.append(Paragraph(f"• {r}", styles["Normal"]))

            # Meta Info
            meta = persona.get("_meta", {})
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"<i>Model:</i> {meta.get('model', '')} | "
                f"<i>Tokens:</i> {meta.get('tokens', 0)} | "
                f"<i>Cost:</i> ${meta.get('cost_usd', 0):.4f} | "
                f"<i>Batch Mode:</i> {meta.get('batchMode', '')}",
                styles["Small"]
            ))
            story.append(Spacer(1, 12))

        # ----- ACCESSIBILITY -----
        acc = result.get("accessibility")
        if acc:
            story.append(Paragraph("Accessibility Review", styles["Heading3"]))
            story.append(Paragraph(f"Score: <b>{acc.get('score', '-')}/100</b>", styles["Normal"]))
            story.append(Spacer(1, 6))

            issues = acc.get("issues", [])
            if issues:
                for i in issues:
                    story.append(Paragraph(
                        f"<b>Issue:</b> {i.get('description', '')}<br/>"
                        f"<b>WCAG:</b> {i.get('wcag_rule', '')}<br/>"
                        f"<b>Impact:</b> {i.get('impact', '')} | <b>Effort:</b> {i.get('effort', '')}<br/>"
                        f"<b>Suggestion:</b> {i.get('suggestion', '')}",
                        styles["Normal"]
                    ))
                    story.append(Spacer(1, 4))

            meta = acc.get("_meta", {})
            story.append(Paragraph(
                f"<i>Model:</i> {meta.get('model', '')} | "
                f"<i>Tokens:</i> {meta.get('tokens', 0)} | "
                f"<i>Cost:</i> ${meta.get('cost_usd', 0):.4f} | "
                f"<i>Batch Mode:</i> {meta.get('batchMode', '')}",
                styles["Small"]
            ))

        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


@router.get("/project/{project_id}/export-pdf")
def export_project_pdf(project_id: str):
    from main import supabase  # lazy import to avoid circular

    data = supabase.table("projects").select("*").eq("id", project_id).single().execute().data
    if not data:
        raise HTTPException(status_code=404, detail="Project not found")

    screens = supabase.table("screens").select("*").eq("project_id", project_id).execute().data
    analysis = supabase.table("analysis_results").select("*").eq("project_id", project_id).execute().data

    payload = {
        "project": data,
        "screens": screens,
        "analysis": analysis
    }

    pdf_data = build_pdf(payload)

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={project_id}.pdf"
        }
    )
