import os
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from django.conf import settings

def generate_rfq_pdf(rfq):
    """
    Generate a PDF for an RFQ.
    Returns the PDF as a BytesIO object.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"Request for Quotation (RFQ) - {rfq.id}", title_style))
    elements.append(Spacer(1, 20))
    
    # Details Table
    details_data = [
        ['Title:', rfq.title],
        ['Category:', rfq.category],
        ['Tower:', rfq.tower],
        ['Estimated Value:', f"₹{rfq.estimated_value:,.2f}" if rfq.estimated_value else "N/A"],
        ['Status:', rfq.status.upper()],
        ['Created By:', rfq.created_by],
        ['Created Date:', str(rfq.created_date.strftime('%Y-%m-%d')) if rfq.created_date else "N/A"],
    ]
    
    details_table = Table(details_data, colWidths=[120, 400])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    # Items
    if getattr(rfq, 'items', None):
        elements.append(Paragraph("Items/Services Required:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        items_data = [['Item Name', 'Description', 'Quantity']]
        for item in rfq.items:
            items_data.append([
                str(item.get('itemName', 'Item')),
                str(item.get('description', '')),
                str(item.get('quantity', 1))
            ])
            
        items_table = Table(items_data, colWidths=[200, 250, 70])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(items_table)
        
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_po_pdf(po):
    """
    Generate a PDF for a Purchase Order.
    Returns the PDF as a BytesIO object.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"Purchase Order (PO) - {po.id}", title_style))
    elements.append(Spacer(1, 20))
    
    # Details Table
    details_data = [
        ['Type:', str(po.type).upper()],
        ['Vendor Name:', po.vendor_name],
        ['Linked RFQ:', str(po.linked_rfq) if po.linked_rfq else "N/A"],
        ['Tower:', po.tower],
        ['Category:', po.category],
        ['Net Value:', f"₹{po.net_value:,.2f}" if po.net_value else "N/A"],
        ['Start Date:', str(po.start_date) if po.start_date else "N/A"],
        ['End Date:', str(po.end_date) if po.end_date else "N/A"],
    ]
    
    details_table = Table(details_data, colWidths=[120, 400])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    # Items
    if getattr(po, 'items', None):
        elements.append(Paragraph("Order Items:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        items_data = [['Item Name', 'Quantity', 'Rate', 'Amount']]
        for item in po.items:
            items_data.append([
                str(item.get('itemName', 'Item')),
                str(item.get('quantity', 1)),
                f"₹{float(item.get('rate', 0)):,.2f}",
                f"₹{float(item.get('amount', 0)):,.2f}",
            ])
            
        items_table = Table(items_data, colWidths=[220, 80, 100, 120])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(items_table)
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
