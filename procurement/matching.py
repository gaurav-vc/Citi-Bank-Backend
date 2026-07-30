import logging
from django.apps import apps

logger = logging.getLogger(__name__)

def run_document_match(invoice):
    """
    Runs 2-Way or 3-Way matching logic on the invoice.
    Updates and returns (matching_status, mismatch_reasons, check_results)
    """
    Invoice = apps.get_model('procurement.Invoice')
    PurchaseOrder = apps.get_model('procurement.PurchaseOrder')
    GRN = apps.get_model('inventory.GRN')

    reasons = []
    checks = {
        'duplicate_check': 'PASSED',
        'vendor_match': 'PASSED',
        'price_validation': 'PASSED',
        'quantity_validation': 'PASSED',
        'grn_existence': 'PASSED',
    }

    # 1. Duplicate check
    dups = Invoice.objects.filter(
        vendor_id=invoice.vendor_id, 
        invoice_number=invoice.invoice_number
    ).exclude(id=invoice.id)
    if dups.exists():
        checks['duplicate_check'] = 'FAILED'
        reasons.append(f"Duplicate invoice: Invoice number '{invoice.invoice_number}' already exists for this vendor.")

    # 2. Retrieve PO
    try:
        po = PurchaseOrder.objects.get(id=invoice.po_id)
    except PurchaseOrder.DoesNotExist:
        checks['vendor_match'] = 'FAILED'
        reasons.append(f"PO Reference '{invoice.po_id}' not found.")
        return 'mismatch', reasons, checks

    # 3. Vendor check
    if invoice.vendor_id != po.vendor:
        checks['vendor_match'] = 'FAILED'
        reasons.append(f"Vendor mismatch: Invoice vendor '{invoice.vendor_id}' does not match PO vendor '{po.vendor}'.")

    # Determine matching type (Material PO -> 3-Way, Service / AMC -> 2-Way)
    is_service = po.type in ('service', 'amc')
    
    # 4. Price and Tax checks (Tolerance check: 5% or Max ₹1000)
    # We only flag if the invoice is HIGHER than the PO. Lower invoices (partial billings) are permitted.
    invoice_val = float(invoice.total_amount)
    po_val = float(po.net_value)
    
    if invoice_val > po_val:
        diff = invoice_val - po_val
        pct_diff = (diff / po_val) * 100 if po_val > 0 else 0
        
        if diff > 1000.0 or pct_diff > 5.0:
            checks['price_validation'] = 'FAILED'
            reasons.append(f"Price discrepancy: Invoice total (₹{invoice_val:,.2f}) exceeds PO value (₹{po_val:,.2f}) beyond tolerance.")

    if is_service:
        # 2-Way Match Result
        status = 'failed' if reasons else '2way'
        return status, reasons, checks

    # 5. Material PO requires GRN (3-Way Matching)
    grn = None
    if invoice.grn_id:
        try:
            grn = GRN.objects.get(id=invoice.grn_id)
        except GRN.DoesNotExist:
            pass
            
    if not grn:
        # Fallback: look for any GRN under this PO
        grn = GRN.objects.filter(po_id=po.id).first()

    if not grn:
        checks['grn_existence'] = 'FAILED'
        reasons.append(f"GRN Missing: Material PO '{po.id}' requires associated GRN.")
        return 'failed', reasons, checks

    # 6. Quantity matching
    po_items = po.items if isinstance(po.items, list) else []
    grn_items = grn.items if isinstance(grn.items, list) else []
    
    po_qty_total = sum(float(i.get('quantity', i.get('qty', 0))) for i in po_items)
    grn_qty_total = sum(float(i.get('accepted_qty', i.get('acceptedQty', 0))) for i in grn_items)
    
    if grn_qty_total <= 0 or grn_qty_total != po_qty_total:
        checks['quantity_validation'] = 'FAILED'
        reasons.append(f"Quantity mismatch: PO ordered {po_qty_total}, but GRN accepted {grn_qty_total}.")

    status = 'failed' if reasons else '3way'
    return status, reasons, checks
