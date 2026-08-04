import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Define cohesive color scheme
COLOR_PRIMARY = colors.HexColor("#1E293B")     # Dark Slate
COLOR_SECONDARY = colors.HexColor("#475569")   # Muted Slate
COLOR_ACCENT = colors.HexColor("#0284C7")      # Bright Blue
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")    # Cool White/Grey
COLOR_BORDER = colors.HexColor("#E2E8F0")      # Border Grey
COLOR_SUCCESS = colors.HexColor("#16A34A")     # Forest Green
COLOR_WARNING = colors.HexColor("#EA580C")     # Amber
COLOR_DANGER = colors.HexColor("#DC2626")      # Red
COLOR_TEXT = colors.HexColor("#0F172A")        # Dark Charcoal

def generate_resume_report(resume_name: str, job_title: str, score_details: Dict[str, Any], llm_details: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a beautifully structured PDF analysis report.
    Returns the PDF as a BytesIO stream.
    """
    pdf_buffer = io.BytesIO()
    
    # Initialize Document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=54, # 0.75 inch
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    
    # Initialize Styles
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=COLOR_PRIMARY
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=COLOR_PRIMARY,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_TEXT
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_TEXT,
        leftIndent=15,
        firstLineIndent=-10
    )
    
    # Header Section
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Spacer(1, 4))
    
    # Metadata Row (Job Title, Date)
    current_date = datetime.now().strftime("%B %d, %Y")
    metadata_text = f"<b>Target Role:</b> {job_title} | <b>Date:</b> {current_date} | <b>File:</b> {resume_name}"
    story.append(Paragraph(metadata_text, subtitle_style))
    story.append(Spacer(1, 15))
    
    # Add horizontal rule
    hr_table = Table([[""]], colWidths=[504])
    hr_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, COLOR_ACCENT),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(hr_table)
    story.append(Spacer(1, 20))
    
    # --- SECTION 1: ATS SCORE & OVERVIEW ---
    score = score_details["ats_score"]
    if score >= 75:
        score_color = COLOR_SUCCESS
        score_desc = "Strong Match"
    elif score >= 50:
        score_color = COLOR_WARNING
        score_desc = "Moderate Match"
    else:
        score_color = COLOR_DANGER
        score_desc = "Low Match"
        
    # Table layout for Score Box and Recommendation
    score_html = f"<font size='36' color='{score_color.hexval()}'><b>{score}%</b></font><br/><font size='10' color='{COLOR_SECONDARY.hexval()}'>ATS Score</font>"
    score_p = Paragraph(score_html, ParagraphStyle('ScoreP', parent=body_style, alignment=1)) # Centered
    
    rec_html = f"<b>Hiring Recommendation:</b> <font color='{score_color.hexval()}'><b>{llm_details.get('hiring_recommendation', 'N/A')}</b></font><br/><br/>{llm_details.get('hiring_explanation', '')}"
    rec_p = Paragraph(rec_html, body_style)
    
    overview_table = Table([[score_p, rec_p]], colWidths=[120, 384])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COLOR_BG_LIGHT),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    
    story.append(Paragraph("Executive Match Summary", h1_style))
    story.append(overview_table)
    story.append(Spacer(1, 20))
    
    # --- SECTION 2: CANDIDATE PROFILE MATRIX ---
    story.append(Paragraph("Profile Extraction Details", h1_style))
    
    cand_exp = f"{score_details['candidate_experience']} years"
    req_exp = f"{score_details['required_experience']} years" if score_details['required_experience'] > 0 else "Not Specified"
    
    matrix_data = [
        [Paragraph("<b>Detected Education</b>", body_style), Paragraph(score_details["candidate_education"], body_style),
         Paragraph("<b>Target Education</b>", body_style), Paragraph(score_details["required_education"], body_style)],
        [Paragraph("<b>Detected Experience</b>", body_style), Paragraph(cand_exp, body_style),
         Paragraph("<b>Target Experience</b>", body_style), Paragraph(req_exp, body_style)]
    ]
    
    matrix_table = Table(matrix_data, colWidths=[120, 132, 120, 132])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COLOR_BG_LIGHT),
        ('BACKGROUND', (2,0), (2,0), COLOR_BG_LIGHT),
        ('BACKGROUND', (0,1), (0,1), COLOR_BG_LIGHT),
        ('BACKGROUND', (2,1), (2,1), COLOR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 20))
    
    # --- SECTION 3: SKILLS GAP ANALYSIS ---
    story.append(Paragraph("Skills Gap Analysis", h1_style))
    
    matched_skills_text = ", ".join(score_details["matched_skills"]) if score_details["matched_skills"] else "None"
    missing_skills_text = ", ".join(score_details["missing_skills"]) if score_details["missing_skills"] else "None"
    
    skills_data = [
        [
            Paragraph("<b>Matching Skills</b>", ParagraphStyle('MHeader', parent=body_style, textColor=COLOR_SUCCESS)),
            Paragraph("<b>Missing Skills Required</b>", ParagraphStyle('WHeader', parent=body_style, textColor=COLOR_WARNING))
        ],
        [
            Paragraph(matched_skills_text, body_style),
            Paragraph(missing_skills_text, body_style)
        ]
    ]
    
    skills_table = Table(skills_data, colWidths=[252, 252])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 20))
    
    # --- SECTION 4: STRENGTHS & WEAKNESSES ---
    sw_flowables = []
    sw_flowables.append(Paragraph("Strengths & Weaknesses", h1_style))
    
    sw_data = []
    
    # Strengths column
    strengths_html = ""
    for s in llm_details.get("strengths", []):
        strengths_html += f"&bull; {s}<br/><br/>"
    if not strengths_html:
        strengths_html = "No strengths listed."
        
    # Weaknesses column
    weaknesses_html = ""
    for w in llm_details.get("weaknesses", []):
        weaknesses_html += f"&bull; {w}<br/><br/>"
    if not weaknesses_html:
        weaknesses_html = "No weaknesses listed."
        
    sw_data.append([
        Paragraph("<b>Key Strengths</b>", ParagraphStyle('SHeader', parent=body_style, textColor=COLOR_SUCCESS)),
        Paragraph("<b>Areas for Development</b>", ParagraphStyle('WeHeader', parent=body_style, textColor=COLOR_DANGER))
    ])
    sw_data.append([
        Paragraph(strengths_html, body_style),
        Paragraph(weaknesses_html, body_style)
    ])
    
    sw_table = Table(sw_data, colWidths=[252, 252])
    sw_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    sw_flowables.append(sw_table)
    story.append(KeepTogether(sw_flowables))
    story.append(Spacer(1, 20))
    
    # --- SECTION 5: RECOMMENDATIONS & IMPROVEMENTS ---
    rec_flowables = []
    rec_flowables.append(Paragraph("Actionable Resume Improvements", h1_style))
    for sug in llm_details.get("suggestions", []):
        rec_flowables.append(Paragraph(f"&bull; <b>Improvement:</b> {sug}", bullet_style))
        rec_flowables.append(Spacer(1, 4))
    if not llm_details.get("suggestions"):
        rec_flowables.append(Paragraph("No specific recommendations generated.", body_style))
        
    story.append(KeepTogether(rec_flowables))
    story.append(Spacer(1, 20))
    
    # --- SECTION 6: RECOMMENDED PROJECTS ---
    proj_flowables = []
    proj_flowables.append(Paragraph("Recommended Skill-Bridging Projects", h1_style))
    
    for idx, proj in enumerate(llm_details.get("recommended_projects", [])):
        title = proj.get("title", f"Project Heuristic {idx+1}")
        desc = proj.get("description", "")
        stack = ", ".join(proj.get("tech_stack", []))
        steps = proj.get("implementation_steps", [])
        
        proj_html = f"<b>{idx+1}. {title}</b> ({stack})<br/>{desc}"
        proj_flowables.append(Paragraph(proj_html, body_style))
        proj_flowables.append(Spacer(1, 10))
        
    if not llm_details.get("recommended_projects"):
        proj_flowables.append(Paragraph("No projects recommended.", body_style))
        
    story.append(KeepTogether(proj_flowables))
    
    # Build Document
    doc.build(story)
    
    # Reset stream pointer
    pdf_buffer.seek(0)
    return pdf_buffer
