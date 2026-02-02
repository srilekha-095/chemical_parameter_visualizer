import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt

def analyze_csv(file_path):
    df = pd.read_csv(file_path)

    summary = {
        "total_equipment": len(df),
        "average_flowrate": round(df["Flowrate"].mean(), 2),
        "average_pressure": round(df["Pressure"].mean(), 2),
        "average_temperature": round(df["Temperature"].mean(), 2),
        "equipment_type_distribution": df["Type"].value_counts().to_dict()
    }

    return summary


def generate_pdf_report(summary, dataset_id):
    """Generate a PDF report from dataset summary"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    # Title
    title = Paragraph("Chemical Equipment Analysis Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Meta information
    meta_data = [
        ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ['Dataset ID:', f'#{dataset_id}'],
        ['Report Type:', 'Equipment Distribution Analysis']
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary section
    elements.append(Paragraph("Summary Statistics", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment', str(summary['total_equipment'])],
        ['Average Flowrate', f"{summary['average_flowrate']:.2f}"],
        ['Average Pressure', f"{summary['average_pressure']:.2f}"],
        ['Average Temperature', f"{summary['average_temperature']:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Equipment distribution
    elements.append(Paragraph("Equipment Type Distribution", heading_style))
    
    distribution = summary['equipment_type_distribution']
    dist_data = [['Equipment Type', 'Count', 'Percentage']]
    total = sum(distribution.values())
    
    for equipment_type, count in distribution.items():
        percentage = (count / total) * 100
        dist_data.append([str(equipment_type), str(count), f"{percentage:.1f}%"])
    
    dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    dist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    elements.append(dist_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = Paragraph(
        "This report was automatically generated by Chemical Equipment Visualizer",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, 
                      textColor=colors.HexColor('#9ca3af'), alignment=1)
    )
    elements.append(footer_text)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer