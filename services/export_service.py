"""
Export services for PDF and CSV generation.
"""
from io import BytesIO, StringIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import csv


def generate_pdf_report(test_requests, test_results, filters=None):
    """
    Generate PDF report for test requests and results.
    
    Args:
        test_requests: QuerySet of TestRequest objects
        test_results: QuerySet of TestResult objects
        filters: Dictionary of applied filters
        
    Returns:
        BytesIO: PDF buffer
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("QMS Test Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Date
    date_str = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    date_para = Paragraph(date_str, styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary Statistics
    total_tests = test_requests.count()
    passed = test_results.filter(pass_fail_status=True).count()
    failed = test_results.filter(pass_fail_status=False).count()
    
    summary_data = [
        ['Total Tests', str(total_tests)],
        ['Passed', str(passed)],
        ['Failed', str(failed)],
        ['Pass Rate', f"{(passed/(passed+failed)*100) if (passed+failed) > 0 else 0:.2f}%"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Test Results Table
    results_data = [['Batch Number', 'Product', 'Parameter', 'Value', 'Status']]
    for result in test_results.select_related('test_request', 'test_request__product', 'parameter')[:100]:
        status = 'Pass' if result.pass_fail_status else 'Fail' if result.pass_fail_status is False else 'Pending'
        results_data.append([
            result.test_request.batch_number,
            result.test_request.product.name,
            result.parameter.name,
            str(result.actual_value),
            status
        ])
    
    if len(results_data) > 1:
        results_table = Table(results_data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1*inch, 0.8*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(Paragraph("Test Results", styles['Heading2']))
        elements.append(results_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_csv_report(test_requests, test_results):
    """
    Generate CSV report for test requests and results.
    
    Args:
        test_requests: QuerySet of TestRequest objects
        test_results: QuerySet of TestResult objects
        
    Returns:
        BytesIO: CSV buffer (encoded as bytes)
    """
    # Use StringIO for text-based CSV writing
    string_buffer = StringIO()
    writer = csv.writer(string_buffer)
    
    # Write header
    writer.writerow(['Batch Number', 'Product', 'Parameter', 'Actual Value', 'Status', 'Test Date'])
    
    # Write data
    for result in test_results.select_related('test_request', 'test_request__product', 'parameter'):
        status = 'Pass' if result.pass_fail_status else 'Fail' if result.pass_fail_status is False else 'Pending'
        writer.writerow([
            result.test_request.batch_number,
            result.test_request.product.name,
            result.parameter.name,
            str(result.actual_value),
            status,
            result.test_request.sample_date.strftime('%Y-%m-%d')
        ])
    
    # Convert StringIO to BytesIO for HTTP response
    csv_content = string_buffer.getvalue()
    string_buffer.close()
    
    # Create BytesIO buffer with UTF-8 encoded content
    buffer = BytesIO()
    buffer.write(csv_content.encode('utf-8-sig'))  # utf-8-sig adds BOM for Excel compatibility
    buffer.seek(0)
    return buffer

