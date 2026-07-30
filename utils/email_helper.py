import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def get_document_link(module, document_id):
    """
    Generates a direct portal link for a document or page.
    """
    frontend_url = 'https://procurement.vibesandbox.live'
    
    m_name = module.lower().replace('-', '_').rstrip('s')
    
    if m_name in ('payment_proposal', 'payment_proposals', 'payment'):
        path = f"/payments/proposals/{document_id}"
    elif m_name in ('invoice', 'invoices', 'billing'):
        path = f"/billing/invoices/{document_id}"
    elif m_name in ('rfq', 'rfqs'):
        path = f"/rfqs/{document_id}"
    elif m_name in ('purchase_order', 'purchase_orders', 'order', 'orders'):
        path = f"/orders/{document_id}"
    elif m_name in ('grn', 'grns'):
        path = f"/grns/{document_id}"
    elif m_name in ('indent', 'indents', 'requisition', 'requisitions'):
        path = f"/indents/{document_id}"
    elif m_name == 'login':
        path = "/login"
    else:
        path = "/dashboard"
        
    return f"{frontend_url}{path}"


def generate_portal_link(module_name, entity_id):
    """
    Generates a direct portal link for a document or page.
    """
    return get_document_link(module_name, entity_id)



def get_email_base_html(title, content_html):
    """
    Returns an HTML email wrapper with FIFC Branding and the required footer.
    """
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#F3F4F6;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05);">
          <!-- Header (FIFC Branding) -->
          <tr>
            <td style="background:linear-gradient(135deg,#1B365D 0%,#2A4E7F 100%);padding:24px 30px;text-align:center;">
              <div style="font-size:20px;font-weight:750;color:#ffffff;letter-spacing:1px;margin:0;">
                FIFC
              </div>
              <div style="font-size:11px;color:#D1D5DB;margin-top:4px;letter-spacing:0.5px;text-transform:uppercase;">
                Procurement & Contract Management
              </div>
            </td>
          </tr>
          
          <!-- Content Body -->
          <tr>
            <td style="padding:30px 30px 20px;color:#1F2937;font-size:15px;line-height:1.6;">
              <h2 style="color:#1B365D;font-size:18px;margin-top:0;margin-bottom:16px;font-weight:700;">{title}</h2>
              {content_html}
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="background-color:#F9FAFB;padding:20px 30px;text-align:center;border-top:1px solid #E5E7EB;color:#9CA3AF;font-size:12px;">
              <p style="margin:0 0 4px 0;">This is an automated email. Please do not reply.</p>
              <p style="margin:0;">&copy; 2026 FIFC. All rights reserved.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

def send_onboarding_email(email=None, name=None, password=None, role=None, org_name=None, site_name=None, temp_password=None, user=None):
    """
    Universal onboarding sender covering Trigger 1 & Trigger 2.
    """
    if user:
        if not email:
            email = user.email
        if not name:
            name = user.name
        if not role:
            role = user.role
        profile = getattr(user, 'profile', None)
        if profile:
            if not org_name and profile.organization:
                org_name = profile.organization.name
            if not site_name and profile.site:
                site_name = profile.site.name

    if temp_password:
        password = temp_password
    if not password:
        password = "Demo@123"

    login_url = get_document_link('login', '')
    
    if org_name and site_name:
        # Trigger 1: Organization Admin
        title = "Organization Admin Portal Activation"
        content_html = f"""
        <p>Dear {name},</p>
        <p>Your Organization Admin account has been successfully provisioned on the FIFC Procurement platform.</p>
        <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
          <p style="margin:0 0 6px 0;"><strong>Name:</strong> {name}</p>
          <p style="margin:0 0 6px 0;"><strong>Role:</strong> {role}</p>
          <p style="margin:0 0 6px 0;"><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
          <p style="margin:0 0 6px 0;"><strong>Password:</strong> {password}</p>
          <p style="margin:0 0 6px 0;"><strong>Organization:</strong> {org_name}</p>
          <p style="margin:0;"><strong>Site/Project:</strong> {site_name}</p>
        </div>
        <p>Please use these credentials to log in to the Procurement Management System.</p>
        <div style="text-align:center;margin:30px 0 10px 0;">
          <a href="{login_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Login to Portal</a>
        </div>
        """
    else:
        # Trigger 2: Regular Employee
        title = "FIFC Employee Account Provisioned"
        content_html = f"""
        <p>Dear {name},</p>
        <p>Your team member account has been successfully provisioned on the FIFC Procurement platform.</p>
        <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
          <p style="margin:0 0 6px 0;"><strong>Name:</strong> {name}</p>
          <p style="margin:0 0 6px 0;"><strong>Role:</strong> {role}</p>
          <p style="margin:0 0 6px 0;"><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
          <p style="margin:0 0 6px 0;"><strong>Password:</strong> {password}</p>
        </div>
        <p>Please use these credentials to log in to the Procurement Management System.</p>
        <div style="text-align:center;margin:30px 0 10px 0;">
          <a href="{login_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Login to Portal</a>
        </div>
        """
        
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=title,
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <onboarding@resend.dev>'),
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False
    )

def send_employee_onboarding_email(email=None, name=None, password=None, role=None, temp_password=None, user=None):
    """
    Trigger 2: Employee Creation Email with dynamic values from saved user record.
    """
    if user:
        if not email:
            email = user.email
        if not name:
            name = user.name
        if not role:
            role = user.role

    if temp_password:
        password = temp_password
    if not password:
        password = "Demo@123"

    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not user and email:
        user = User.objects.filter(email=email).first()
    
    org_name = ""
    site_name = ""
    saved_role = role
    
    if user:
        saved_role = user.role
        profile = getattr(user, 'profile', None)
        if profile:
            if profile.organization:
                org_name = profile.organization.name
            if profile.site:
                site_name = profile.site.name
                
    assigned_organization = f"{org_name} / {site_name}" if site_name else org_name
    if not assigned_organization:
        assigned_organization = "CampusSpend Headquarters"
        
    frontend_login_url = get_document_link('login', '')
    
    # Text content
    plain_message = f"""Your account has been created successfully.

Email: {email}
Password: {password}
Role: {saved_role}

Please use these credentials to log in to the Procurement Management System."""

    # HTML content
    content_html = f"""
    <p>Your account has been created successfully.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>Name:</strong> {name}</p>
      <p style="margin:0 0 6px 0;"><strong>Role:</strong> {saved_role}</p>
      <p style="margin:0 0 6px 0;"><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
      <p style="margin:0 0 6px 0;"><strong>Password:</strong> {password}</p>
    </div>
    <p>Please use these credentials to log in to the Procurement Management System.</p>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{frontend_login_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Login to Portal</a>
    </div>
    """
    html_message = get_email_base_html("Welcome to CampusSpend", content_html)
    
    send_mail(
        subject="Welcome to CampusSpend",
        message=plain_message,
        from_email="noreply.procurementdemo@gmail.com",
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False
    )

def send_rfq_creation_email(rfq, creator_email):
    """
    Send RFQ details with PDF when RFQ is created.
    """
    from django.core.mail import EmailMultiAlternatives
    from utils.pdf_generator import generate_rfq_pdf
    
    title = f"New Request for Quotation (RFQ) Created - {rfq.id}"
    content_html = f"""
    <p>Dear User,</p>
    <p>A new Request for Quotation (RFQ) has been successfully created.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>RFQ Number:</strong> {rfq.id}</p>
      <p style="margin:0 0 6px 0;"><strong>Title:</strong> {rfq.title}</p>
      <p style="margin:0 0 6px 0;"><strong>Category:</strong> {rfq.category}</p>
      <p style="margin:0;"><strong>Estimated Value:</strong> ₹{rfq.estimated_value:,.2f}</p>
    </div>
    <p>Please find the RFQ details document attached as a PDF.</p>
    """
    
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    msg = EmailMultiAlternatives(
        subject=title,
        body=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        to=[creator_email]
    )
    msg.attach_alternative(html_message, "text/html")
    
    # Generate and attach PDF
    try:
        pdf_buffer = generate_rfq_pdf(rfq)
        msg.attach(f'{rfq.id}_details.pdf', pdf_buffer.getvalue(), 'application/pdf')
    except Exception as e:
        logger.error(f"Failed to attach PDF to RFQ email: {e}")
        
    try:
        msg.send(fail_silently=False)
    except Exception as e:
        logger.error(f"Failed to send RFQ creation email: {e}")

def send_po_creation_email(po):
    """
    Send PO details with PDF when PO is created.
    """
    from django.core.mail import EmailMultiAlternatives
    from utils.pdf_generator import generate_po_pdf
    from vendors.models import Vendor
    
    vendor_email = None
    vendor_name = po.vendor_name
    try:
        vendor = Vendor.objects.get(id=po.vendor)
        vendor_email = vendor.email
    except Exception:
        # Check if email is in vendor field
        if '@' in po.vendor:
            vendor_email = po.vendor
            
    if not vendor_email:
        logger.error(f"Cannot send PO email for {po.id}: No vendor email found.")
        return

    title = f"New Purchase Order (PO) Created - {po.id}"
    content_html = f"""
    <p>Dear {vendor_name},</p>
    <p>A new Purchase Order (PO) has been generated for you.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>PO Number:</strong> {po.id}</p>
      <p style="margin:0 0 6px 0;"><strong>Tower:</strong> {po.tower}</p>
      <p style="margin:0 0 6px 0;"><strong>Category:</strong> {po.category}</p>
      <p style="margin:0;"><strong>Net Value:</strong> ₹{po.net_value:,.2f}</p>
    </div>
    <p>Please find the official Purchase Order document attached as a PDF.</p>
    """
    
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    msg = EmailMultiAlternatives(
        subject=title,
        body=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        to=[vendor_email]
    )
    msg.attach_alternative(html_message, "text/html")
    
    try:
        pdf_buffer = generate_po_pdf(po)
        msg.attach(f'{po.id}_details.pdf', pdf_buffer.getvalue(), 'application/pdf')
    except Exception as e:
        logger.error(f"Failed to attach PDF to PO email: {e}")
        
    try:
        msg.send(fail_silently=False)
    except Exception as e:
        logger.error(f"Failed to send PO creation email: {e}")


def send_rfq_vendor_invitation_email(vendor_email, vendor_name, rfq_id, category, details, deadline):
    """
    Trigger 3: RFQ Vendor Invitation Email.
    """
    login_url = get_document_link('login', '')
    title = f"Invitation to Quote: RFQ {rfq_id}"
    content_html = f"""
    <p>Dear {vendor_name},</p>
    <p>You are formally invited to submit a quotation for the following requirement at FIFC.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>RFQ Number:</strong> {rfq_id}</p>
      <p style="margin:0 0 6px 0;"><strong>Category:</strong> {category}</p>
      <p style="margin:0 0 6px 0;"><strong>Requirement Details:</strong> {details}</p>
      <p style="margin:0;"><strong>Submission Deadline:</strong> <span style="color:#DC2626;font-weight:700;">{deadline}</span></p>
    </div>
    <p>Please log in to your vendor portal account to view the full specification and upload your commercial proposal.</p>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{login_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Access Vendor Portal</a>
    </div>
    """
    
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=title,
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        recipient_list=[vendor_email],
        html_message=html_message,
        fail_silently=False
    )

def send_vendor_award_notification_email(vendor_email, vendor_name, rfq_id, po_id, quote_value, delivery_date):
    """
    Trigger 4: Vendor Award Email.
    """
    # Build download link pointing to backend PDF endpoint
    frontend_url = 'https://procurement.vibesandbox.live'
    backend_base = frontend_url.replace(':8080', ':8000').replace(':5173', ':8000').replace(':3000', ':8000')
    download_url = f"{backend_base}/api/orders/{po_id}/download/"
    rfq_url = get_document_link('rfq', rfq_id)
    
    title = f"Contract Award Notification - RFQ {rfq_id}"
    content_html = f"""
    <p>Dear {vendor_name},</p>
    <p>We are pleased to inform you that your quotation has been selected and awarded for <strong>RFQ {rfq_id}</strong>. The commercial terms and delivery schedule have been finalized.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>RFQ Reference:</strong> {rfq_id}</p>
      <p style="margin:0 0 6px 0;"><strong>Purchase Order Number:</strong> {po_id}</p>
      <p style="margin:0 0 6px 0;"><strong>Awarded Order Value:</strong> ₹{quote_value:,.2f}</p>
      <p style="margin:0;"><strong>Target Delivery Date:</strong> {delivery_date}</p>
    </div>
    <p>You can download the official Purchase Order document or view the award details in the portal:</p>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{download_url}" style="background-color:#6B7280;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;margin-right:10px;">Download Purchase Order (PDF)</a>
      <a href="{rfq_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">View Award</a>
    </div>
    """
    
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=title,
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        recipient_list=[vendor_email],
        html_message=html_message,
        fail_silently=False
    )

def send_vendor_onboarding_email(email, name, temp_password):
    """
    Vendor Onboarding & Credentials Email.
    """
    login_url = get_document_link('login', '')
    title = "Welcome to Procurement Management System"
    
    plain_message = f"""Welcome to Procurement Management System

Vendor Name: {name}
Login URL: {login_url}
User ID: {email}
Temporary Password: {temp_password}

Please change your password after your first login."""

    content_html = f"""
    <p>Welcome to Procurement Management System</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>Vendor Name:</strong> {name}</p>
      <p style="margin:0 0 6px 0;"><strong>User ID:</strong> {email}</p>
      <p style="margin:0 0 6px 0;"><strong>Temporary Password:</strong> <code style="background-color:#E5E7EB;padding:2px 6px;border-radius:4px;font-weight:700;">{temp_password}</code></p>
    </div>
    <p>Please change your password after your first login.</p>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{login_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">Login to Portal</a>
    </div>
    """
    html_message = get_email_base_html(title, content_html)
    
    send_mail(
        subject="Welcome to Procurement Management System",
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False
    )

def send_invoice_rejection_email(vendor_email, vendor_name, invoice_number, reason):
    """
    Invoice Rejection Notification Email.
    """
    invoice_url = get_document_link('invoice', invoice_number)
    title = f"Invoice Rejection Notification - {invoice_number}"
    content_html = f"""
    <p>Dear {vendor_name},</p>
    <p>Invoice approval has been rejected due to internal review.</p>
    <p>The invoice will not proceed for payment at this time.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>Invoice Number:</strong> {invoice_number}</p>
      <p style="margin:0;"><strong>Rejection Reason:</strong> {reason}</p>
    </div>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{invoice_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">View Invoice</a>
    </div>
    """
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=title,
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        recipient_list=[vendor_email],
        html_message=html_message,
        fail_silently=False
    )

def send_vendor_payment_notification_email(vendor_email, proposal_id, net_payable, utr_number):
    """
    Vendor Payment Processing Notification Email.
    """
    proposal_url = get_document_link('payment_proposal', proposal_id)
    title = f"Payment Advice - Proposal {proposal_id}"
    content_html = f"""
    <p>Dear Partner,</p>
    <p>We are pleased to inform you that a payment has been processed and initiated for your reference.</p>
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>Payment Proposal Reference:</strong> {proposal_id}</p>
      <p style="margin:0 0 6px 0;"><strong>Net Amount Paid:</strong> ₹{float(net_payable):,.2f}</p>
      <p style="margin:0;"><strong>UTR / Transaction Reference:</strong> {utr_number}</p>
    </div>
    <p>Please check your registered bank account for credit confirmations.</p>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{proposal_url}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">View Payment Details</a>
    </div>
    """
    html_message = get_email_base_html(title, content_html)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=title,
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FIFC Procurement <noreply.procurementdemo@gmail.com>'),
        recipient_list=[vendor_email],
        html_message=html_message,
        fail_silently=False
    )


def send_workflow_approval_email(user, module_name, document_id, title, portal_link, created_by='', vendor_name=None, amount=None, stage_name='', action_required='Approval Review Required'):
    """
    Sends an email notification to the next approver for a workflow step.
    """
    from django.core.mail import send_mail
    from django.utils.html import strip_tags
    from django.conf import settings
    
    # Determine if it is a CXO email
    user_role = getattr(user, 'role', '')
    is_cxo = user_role in ('cxo_citi', 'cxo_emb') or 'cxo' in stage_name.lower()
    
    # Map module keys to proper singular names
    module_display_names = {
        'orders': 'Purchase Order',
        'invoices': 'Invoice',
        'payments': 'Payment Proposal',
        'rfqs': 'Request for Quotation',
        'indents': 'Indent/Requisition'
    }
    display_module_name = module_display_names.get(module_name.lower(), module_name.replace('_', ' ').title().rstrip('s'))
    
    if is_cxo:
        subject = f"Executive Approval Required: {title} ({document_id})"
        intro = f"""
        <p>Dear {getattr(user, 'name', getattr(user, 'username', 'Executive'))},</p>
        <p>All preliminary reviews and required team approvals for the following <strong>{display_module_name}</strong> have been successfully completed.</p>
        <p>It is now pending your final executive approval in the Procurement Management System.</p>
        """
    else:
        subject = f"Workflow Action Required: {title} ({document_id})"
        intro = f"""
        <p>Dear {getattr(user, 'name', getattr(user, 'username', 'Approver'))},</p>
        <p>A document has been routed to you and is awaiting your review/approval in the Procurement Management System.</p>
        """
        
    # Format amount if provided
    amount_str = ""
    if amount is not None:
        try:
            amount_str = f"₹{float(amount):,.2f}"
        except Exception:
            amount_str = str(amount)
            
    # Customize button label based on module name
    normalized_mod = module_name.lower().replace('-', '_').rstrip('s')
    if normalized_mod in ('payment_proposal', 'payment_proposals', 'payment'):
        button_label = "Open Payment Proposal"
    else:
        button_label = "Open Document"

    content_html = f"""
    {intro}
    <div style="background-color:#F3F4F6;border:1px solid #E5E7EB;border-radius:6px;padding:15px;margin:20px 0;">
      <p style="margin:0 0 6px 0;"><strong>Document Type:</strong> {display_module_name}</p>
      <p style="margin:0 0 6px 0;"><strong>Document ID:</strong> {document_id}</p>
      <p style="margin:0 0 6px 0;"><strong>Created By:</strong> {created_by}</p>
    """
    if vendor_name:
        content_html += f'<p style="margin:0 0 6px 0;"><strong>Vendor:</strong> {vendor_name}</p>'
    if amount_str:
        content_html += f'<p style="margin:0 0 6px 0;"><strong>Amount:</strong> {amount_str}</p>'
        
    # Fetch additional invoice-specific details if it's an invoice
    if module_name.lower() in ('invoices', 'invoice'):
        try:
            from procurement.models import Invoice
            inv = Invoice.objects.filter(id=document_id).first()
            if inv:
                if getattr(inv, 'invoice_number', None):
                    content_html += f'<p style="margin:0 0 6px 0;"><strong>Invoice No:</strong> {inv.invoice_number}</p>'
                if getattr(inv, 'po_id', None):
                    content_html += f'<p style="margin:0 0 6px 0;"><strong>PO Ref:</strong> {inv.po_id}</p>'
        except Exception:
            pass
        
    content_html += f"""
      <p style="margin:0 0 6px 0;"><strong>Current Stage:</strong> {stage_name}</p>
      <p style="margin:0;"><strong>Action Required:</strong> {action_required}</p>
    </div>
    <div style="text-align:center;margin:30px 0 10px 0;">
      <a href="{portal_link}" style="background-color:#1B365D;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;display:inline-block;">{button_label}</a>
    </div>
    """
    
    html_message = get_email_base_html(subject, content_html)
    plain_message = strip_tags(html_message)
    
    recipient_email = getattr(user, 'email', None)
    if not recipient_email:
        raise ValueError("User object must have a valid email attribute.")
        
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'CampusSpend <noreply.procurementdemo@gmail.com>'),
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Email sending failed: {e}")
        raise



