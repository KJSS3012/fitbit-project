from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Literal
from datetime import datetime
from io import BytesIO, StringIO
import csv

from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.repositories.patient_repository import PatientRepository

router = APIRouter(tags=["Export"])


@router.get("/export")
def export_data(
    format: Literal["pdf", "csv", "json"] = Query(..., description="Export format"),
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export patient health metrics in PDF, CSV or JSON format.
    
    All formats include header with:
    - Patient name and CPF
    - Generation timestamp
    - Period
    
    Args:
        format: Output format (pdf, csv, json)
        start_date: Period start date (YYYY-MM-DD)
        end_date: Period end date (YYYY-MM-DD)
        
    Returns:
        StreamingResponse with file content
        
    Raises:
        400: Invalid period (start > end or > 365 days)
        404: No data available for period
    """
    cpf = current_user["sub"]
    
    # Validate dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use YYYY-MM-DD."
        )
    
    if start_dt > end_dt:
        raise HTTPException(
            status_code=400,
            detail="Período inválido. Verifique as datas informadas."
        )
    
    if end_dt > datetime.now():
        raise HTTPException(
            status_code=400,
            detail="A data final não pode ser posterior à data de hoje."
        )
    
    if (end_dt - start_dt).days > 365:
        raise HTTPException(
            status_code=400,
            detail="O período customizado não pode exceder 365 dias."
        )
    
    # Get patient and metrics
    repo = PatientRepository(db)
    patient = repo.find_by_cpf(cpf)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    metrics = repo.get_metrics(cpf, start_date, end_date)
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="Nenhum dado disponível para o período selecionado"
        )
    
    # Generate header metadata
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    patient_header = f"Paciente: {patient.name} ({cpf})"
    generation_header = f"Gerado em: {generated_at}"
    period_header = f"Período: {start_dt.strftime('%d/%m/%Y')} - {end_dt.strftime('%d/%m/%Y')}"
    
    # Generate file based on format
    if format == "pdf":
        return generate_pdf(metrics, patient_header, generation_header, period_header, cpf)
    elif format == "csv":
        return generate_csv(metrics, patient_header, generation_header, period_header, cpf)
    elif format == "json":
        return generate_json(metrics, patient.name, cpf, generated_at, start_date, end_date)


def generate_pdf(metrics, patient_header: str, generation_header: str, period_header: str, cpf: str):
    """
    Generate PDF report with patient metrics.
    
    Uses reportlab to create formatted PDF with:
    - Header section with patient info and generation time
    - Summary statistics
    - Detailed metrics table
    
    Args:
        metrics: List of PatientMetrics objects
        patient_header: Patient name and CPF line
        generation_header: Generation timestamp line
        period_header: Period range line
        cpf: Patient CPF for filename
        
    Returns:
        StreamingResponse with PDF content
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        # Fallback to simple text-based PDF if reportlab not available
        return generate_simple_pdf(metrics, patient_header, generation_header, period_header, cpf)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=20
    )
    story.append(Paragraph("RELATÓRIO DE DADOS DE SAÚDE", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient info
    info_style = styles['Normal']
    story.append(Paragraph(patient_header, info_style))
    story.append(Paragraph(generation_header, info_style))
    story.append(Paragraph(period_header, info_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary
    story.append(Paragraph("<b>RESUMO</b>", styles['Heading2']))
    story.append(Paragraph(f"Total de registros: {len(metrics)}", info_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metrics table
    story.append(Paragraph("<b>DETALHAMENTO</b>", styles['Heading2']))
    
    table_data = [["Data", "Passos", "FC (bpm)", "Sono (h)", "Calorias"]]
    for m in metrics:
        table_data.append([
            m.date,
            str(m.steps),
            str(m.hr_avg),
            f"{m.sleep_hours:.1f}",
            str(m.calories)
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fitbit_dados_{cpf}_{timestamp}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def generate_simple_pdf(metrics, patient_header: str, generation_header: str, period_header: str, cpf: str):
    """
    Fallback simple text-based PDF generator.
    Used when reportlab is not available.
    """
    content = f"{patient_header}\n{generation_header}\n{period_header}\n\n"
    content += "DADOS DE SAÚDE\n"
    content += "=" * 80 + "\n\n"
    content += f"{'Data':<12} {'Passos':<10} {'FC (bpm)':<10} {'Sono (h)':<10} {'Calorias':<10}\n"
    content += "-" * 80 + "\n"
    
    for m in metrics:
        content += f"{m.date:<12} {m.steps:<10} {m.hr_avg:<10} {m.sleep_hours:<10.1f} {m.calories:<10}\n"
    
    buffer = BytesIO(content.encode('utf-8'))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fitbit_dados_{cpf}_{timestamp}.txt"
    
    return StreamingResponse(
        buffer,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def generate_csv(metrics, patient_header: str, generation_header: str, period_header: str, cpf: str):
    """
    Generate CSV file with metadata header and metrics data.
    
    CSV format includes:
    - Comment lines with patient info (# prefix)
    - Header row with column names
    - Data rows
    
    Args:
        metrics: List of PatientMetrics objects
        patient_header: Patient name and CPF line
        generation_header: Generation timestamp line
        period_header: Period range line
        cpf: Patient CPF for filename
        
    Returns:
        StreamingResponse with CSV content
    """
    output = StringIO()
    
    # Metadata header (as comments)
    output.write(f"# {patient_header}\n")
    output.write(f"# {generation_header}\n")
    output.write(f"# {period_header}\n")
    output.write("#\n")
    
    # CSV data
    writer = csv.writer(output)
    writer.writerow(["Data", "Passos", "Frequência Cardíaca (BPM)", "Sono (horas)", "Calorias"])
    
    for m in metrics:
        writer.writerow([
            m.date,
            m.steps,
            m.hr_avg,
            f"{m.sleep_hours:.1f}",
            m.calories
        ])
    
    output.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fitbit_dados_{cpf}_{timestamp}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def generate_json(metrics, patient_name: str, cpf: str, generated_at: str, start_date: str, end_date: str):
    """
    Generate JSON file with metadata and metrics data.
    
    JSON structure:
    {
      "metadata": {
        "patient_name": str,
        "patient_cpf": str,
        "generated_at": str,
        "period": { "start": str, "end": str }
      },
      "metrics": [ { date, steps, hr_avg, sleep_hours, calories, source } ]
    }
    
    Args:
        metrics: List of PatientMetrics objects
        patient_name: Patient full name
        cpf: Patient CPF
        generated_at: Generation timestamp
        start_date: Period start date
        end_date: Period end date
        
    Returns:
        JSONResponse with structured data
    """
    data = {
        "metadata": {
            "patient_name": patient_name,
            "patient_cpf": cpf,
            "generated_at": generated_at,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "total_records": len(metrics)
        },
        "metrics": [
            {
                "date": m.date,
                "steps": m.steps,
                "hr_avg": m.hr_avg,
                "sleep_hours": m.sleep_hours,
                "calories": m.calories,
                "source": m.source
            }
            for m in metrics
        ]
    }
    
    return JSONResponse(content=data)
