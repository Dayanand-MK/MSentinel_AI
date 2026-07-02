from pathlib import Path
from models import Document
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFReportGenerator:
    def generate(self, document: Document, output_path: Path):
        # Setup document template
        doc = SimpleDocTemplate(
            str(output_path), 
            pagesize=letter,
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Define colors
        primary_color = colors.HexColor("#1A365D")
        secondary_color = colors.HexColor("#2B6CB0")
        accent_color = (
            colors.HexColor("#C53030") if document.risk_score >= 50 
            else (colors.HexColor("#D69E2E") if document.risk_score >= 20 
                  else colors.HexColor("#2F855A"))
        )
        light_bg = colors.HexColor("#F7FAFC")
        text_dark = colors.HexColor("#2D3748")
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=primary_color,
            spaceAfter=15
        )
        
        heading_style = ParagraphStyle(
            'ReportHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=secondary_color,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            textColor=text_dark,
            spaceAfter=8
        )

        header_cell_style = ParagraphStyle(
            'HeaderCell',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.whitesmoke
        )
        
        bullet_style = ParagraphStyle(
            'ReportBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=text_dark,
            leftIndent=20,
            firstLineIndent=-10,
            spaceAfter=5
        )
        
        story = []
        
        # 1. Header Banner
        story.append(Paragraph("🛡️ MSentinel AI Compliance Report", title_style))
        story.append(Spacer(1, 10))
        
        # 2. Document Summary Table
        summary_data = [
            [Paragraph("<b>File Name:</b>", body_style), Paragraph(document.original_name, body_style)],
            [Paragraph("<b>Date Generated:</b>", body_style), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), body_style)],
            [Paragraph("<b>Risk Score:</b>", body_style), Paragraph(f"<font color='{accent_color.hexval()}'><b>{document.risk_score} / 100 ({document.risk_level} Risk)</b></font>", body_style)],
            [Paragraph("<b>Compliance Score:</b>", body_style), Paragraph(f"<b>{document.compliance_score} / 100</b>", body_style)],
            [Paragraph("<b>OCR Processing:</b>", body_style), Paragraph("Yes" if document.ocr_used else "No", body_style)],
        ]
        
        summary_table = Table(summary_data, colWidths=[120, 380])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))
        
        # 3. Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        exec_summary = (
            f"The uploaded document <b>{document.original_name}</b> has been scanned by MSentinel AI's "
            f"multi-layer sensitive data engine. The analysis reveals a cumulative risk score of "
            f"<b>{document.risk_score}</b>, placing the document in the <b>{document.risk_level}</b> risk category. "
            f"The compliance score of <b>{document.compliance_score}</b> reflects the presence of "
            f"{len(document.entities)} detected sensitive data elements. "
            f"Data masking and credentials rotation are advised according to the findings detailed below."
        )
        story.append(Paragraph(exec_summary, body_style))
        story.append(Spacer(1, 10))
        
        # 4. Sensitive Data Findings Table
        story.append(Paragraph("Sensitive Data Summary", heading_style))
        if not document.entities:
            story.append(Paragraph("No sensitive data elements were detected in this document.", body_style))
        else:
            table_data = [[
                Paragraph("Category", header_cell_style),
                Paragraph("Method", header_cell_style),
                Paragraph("Confidence", header_cell_style),
                Paragraph("Risk Weight", header_cell_style),
                Paragraph("Page", header_cell_style),
            ]]
            for entity in document.entities:
                table_data.append([
                    Paragraph(entity.category, body_style),
                    Paragraph(entity.method, body_style),
                    Paragraph(f"{entity.confidence:.2f}", body_style),
                    Paragraph(str(entity.risk_weight), body_style),
                    Paragraph(str(getattr(entity, "page", 1)), body_style),
                ])
            
            findings_table = Table(table_data, colWidths=[150, 100, 80, 100, 70])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ]))
            story.append(findings_table)
        story.append(Spacer(1, 15))
        
        # 5. Recommendations
        story.append(Paragraph("Actionable Recommendations", heading_style))
        if not document.recommendations:
            story.append(Paragraph("No specific recommendations are required for this document.", body_style))
        else:
            for rec in document.recommendations:
                story.append(Paragraph(f"• {rec}", bullet_style))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("<i>End of Compliance Report — Generated by MSentinel AI</i>", body_style))
        
        doc.build(story)
