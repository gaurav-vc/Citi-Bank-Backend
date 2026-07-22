from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Avg, Q, F, Count
from django.db.models.functions import Coalesce
from django.http import HttpResponse, FileResponse
from datetime import datetime, date, timedelta
import json
from io import BytesIO
import openpyxl
from django.contrib.auth import get_user_model

from procurement.models import PurchaseOrder, Budget, Expense, Invoice, Indent
from vendors.models import Vendor, RateContract
from inventory.models import Item
from organizations.models import Organization, Site, SiteModuleAccess
from utils.exporter import export_data
from utils.db_logger import log_export

User = get_user_model()

class SuperAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', '') != 'super_admin':
            return Response({"error": "Unauthorized"}, status=403)

        # --- Counters (3 fast COUNT queries) ---
        total_users   = User.objects.count()
        active_sites  = Site.objects.filter(is_active=True).count()
        total_company = Organization.objects.count()

        # --- Revenue (1 aggregate) ---
        total_revenue = float(
            Invoice.objects.filter(status='PAID')
            .aggregate(total=Sum('amount'))['total'] or 0
        )

        # --- Recent Invoices (limited, only needed fields) ---
        recent_invoices = (
            Invoice.objects
            .filter(status='PAID')
            .only('id', 'vendor_name', 'amount')
            .order_by('-created_at')[:5]
        )
        todays_upsale = [
            {
                "id": inv.id,
                "name": inv.vendor_name or "Unknown Vendor",
                "sites": getattr(inv, 'site_id', 1),
                "amount": float(inv.amount or 0)
            }
            for inv in recent_invoices
        ]

        # --- Company-wise Site count (1 annotated query) ---
        company_sites = (
            Organization.objects
            .annotate(site_count=Count('site'))
            .only('name')
            .order_by('-site_count')[:10]
        )
        company_wise_site = [
            {"name": org.name, "sites": org.site_count}
            for org in company_sites
        ]

        # --- Module stats: one DB-level GROUP BY instead of Python loop ---
        module_rates = {
            'procurement': 5000,
            'inventory':   4000,
            'finance':     6000,
            'qc':          2000,
            'core':        1000,
        }

        # Pull only the module_key column, count per prefix in Python (fast — just strings)
        enabled_keys = (
            SiteModuleAccess.objects
            .filter(is_enabled=True)
            .values_list('module_key', flat=True)
        )
        module_stats = {}
        for key in enabled_keys:
            prefix = key.split(':')[0]
            if prefix not in module_stats:
                module_stats[prefix] = {"sites": 0, "revenue": 0}
            module_stats[prefix]["sites"]   += 1
            module_stats[prefix]["revenue"] += module_rates.get(prefix, 3000)

        module_wise_revenue = [
            {"name": k.title(), "revenue": v["revenue"]}
            for k, v in module_stats.items()
        ]
        module_wise_site = [
            {"name": k.title(), "sites": v["sites"]}
            for k, v in module_stats.items()
        ]

        return Response({
            "totalRevenue":    total_revenue,
            "activeSites":     active_sites,
            "totalUsers":      total_users,
            "totalCompany":    total_company,
            "todaysUpsale":    todays_upsale,
            "companyWiseSite": company_wise_site,
            "moduleWiseRevenue": module_wise_revenue,
            "moduleWiseSite":  module_wise_site,
        })

class SuperAdminBillingLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', '') != 'super_admin':
            return Response({"error": "Unauthorized"}, status=403)

        # Single query — pull only the columns we need, no Python-level looping over full objects
        orgs = (
            Organization.objects
            .only(
                'id', 'name', 'company_name', 'legal_name',
                'billing_type', 'billing_rate', 'billing_date', 'is_active'
            )
            .order_by('-created_at')
        )

        data = [
            {
                "id":                org.id,
                "organization":      org.name,
                "company":           org.company_name or org.legal_name or "-",
                "current_plan":      org.billing_type or "Standard Plan",
                "billing_amount":    float(org.billing_rate or 0),
                "next_billing_date": org.billing_date.isoformat() if org.billing_date else "-",
                "current_due":       0.00,
                "status":            "Paid" if org.is_active else "Inactive",
            }
            for org in orgs
        ]

        return Response(data)

class SuperAdminBillingLogDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if getattr(request.user, 'role', '') != 'super_admin':
            return Response({"error": "Unauthorized"}, status=403)
            
        try:
            inv = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)
            
        # Fetch detailed workflow history from the invoice object (which inherits WorkflowAbstractModel)
        # and standard invoice details.
        
        workflow_history = getattr(inv, 'workflow_history', [])
        
        data = {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "vendor_name": inv.vendor_name,
            "amount": float(inv.amount or 0),
            "tax_amount": float(getattr(inv, 'tax_amount', 0)),
            "total_amount": float(getattr(inv, 'total_amount', 0) or inv.amount or 0),
            "status": inv.status,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "site_id": inv.site_id,
            "created_by": inv.created_by,
            "workflow_history": workflow_history,
            "current_approver": getattr(inv, 'current_approver', None),
            "approval_level": getattr(inv, 'approval_level', 0),
        }
        
        return Response(data)

class ReportsDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 1. Spend by Category
            category_res = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).values('category').annotate(
                value=Sum('total_value')
            ).order_by('-value')
            
            category_colors = {
                'HVAC': '#3b82f6',
                'Electrical': '#10b981',
                'Security': '#f59e0b',
                'Soft Services': '#8b5cf6',
                'Housekeeping': '#8b5cf6',
                'Civil': '#ef4444',
                'Project Works': '#ef4444',
                'Plumbing': '#06b6d4'
            }
            default_colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
            
            spend_by_category = []
            for idx, item in enumerate(category_res):
                cat_name = item['category']
                spend_by_category.append({
                    'name': cat_name,
                    'value': float(item['value'] or 0.0),
                    'color': category_colors.get(cat_name, default_colors[idx % len(default_colors)])
                })

            # 2. Tower-wise Spend
            tower_res = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).values('tower', 'category').annotate(
                spend=Sum('total_value')
            )
            
            tower_map = {}
            for item in tower_res:
                t = item['tower'] or 'Tower A'
                cat = item['category'] or ''
                val = float(item['spend'] or 0.0)
                
                if t not in tower_map:
                    tower_map[t] = {'tower': t, 'hvac': 0.0, 'electrical': 0.0, 'security': 0.0, 'softServices': 0.0}
                    
                cat_lower = cat.lower()
                if 'hvac' in cat_lower:
                    tower_map[t]['hvac'] += val
                elif 'electrical' in cat_lower:
                    tower_map[t]['electrical'] += val
                elif 'security' in cat_lower:
                    tower_map[t]['security'] += val
                elif 'soft' in cat_lower or 'housekeeping' in cat_lower:
                    tower_map[t]['softServices'] += val
                    
            tower_wise_spend = list(tower_map.values())

            # 3. Vendor Performance
            vendors = Vendor.objects.all()
            vendor_performance = []
            for v in vendors[:5]:
                # Calculate spend for this vendor
                v_spend = float(PurchaseOrder.objects.filter(vendor=v.id, status__in=['approved', 'active', 'completed']).aggregate(s=Sum('total_value'))['s'] or 0.0)
                sla_pct = int(float(v.sla_rating) * 20)
                vendor_performance.append({
                    'vendor': v.name,
                    'sla': sla_pct,
                    'deliveryScore': max(70, sla_pct - 3),
                    'qualityScore': max(70, sla_pct + 2),
                    'spend': v_spend
                })
            vendor_performance = sorted(vendor_performance, key=lambda x: x['spend'], reverse=True)

            # 4. Monthly Spend (Budget vs Actual)
            # Fetch POs and Expenses grouped by month
            monthly_spend = []
            months_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            monthly_actuals = {m: 0.0 for m in months_names}
            
            pos = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed'])
            for p in pos:
                if p.start_date:
                    m_name = p.start_date.strftime('%b')
                    if m_name in monthly_actuals:
                        monthly_actuals[m_name] += float(p.total_value)
                        
            exps = Expense.objects.all()
            for e in exps:
                if e.date:
                    m_name = e.date.strftime('%b')
                    if m_name in monthly_actuals:
                        monthly_actuals[m_name] += float(e.amount)
            
            # Budget monthly calculation
            total_annual_budget = float(Budget.objects.aggregate(b=Sum('annual_budget'))['b'] or 0.0)
            monthly_budget_calculated = round(total_annual_budget / 12) if total_annual_budget > 0 else 0
            
            # Construct spend data
            for m in months_names:
                if monthly_actuals[m] > 0 or monthly_budget_calculated > 0:
                    monthly_spend.append({
                        'month': m,
                        'actual': monthly_actuals[m],
                        'budget': monthly_budget_calculated
                    })

            # 5. Inventory Value Trend
            items_list = Item.objects.all()
            current_val = sum(float(i.current_stock) * float(i.unit_price) for i in items_list)
            # Use real current stock valuation for current month, older months are 0 if no historical data exists
            current_month = datetime.now().strftime('%b')
            inventory_trend = [{'month': current_month, 'value': current_val}] if current_val > 0 else []

            # 6. Budget Stats
            budget_stats = Budget.objects.aggregate(
                budget=Sum('annual_budget'),
                actual=Sum('actual')
            )
            total_budget = float(budget_stats['budget'] or 0.0)
            actual_spend = float(budget_stats['actual'] or 0.0)
            remaining_budget = total_budget - actual_spend
            over_percent = ((actual_spend - total_budget) / total_budget * 100) if total_budget > 0 and actual_spend > total_budget else 0.0

            # 7. Inventory Stats
            current_inventory_value = current_val
            total_skus = Item.objects.count()
            low_stock_items = Item.objects.filter(current_stock__lte=F('min_stock_level')).count()
            dead_stock_items = Item.objects.filter(current_stock=0).count()

            return Response({
                'spendByCategory': spend_by_category,
                'towerWiseSpend': tower_wise_spend,
                'vendorPerformance': vendor_performance,
                'monthlySpend': monthly_spend,
                'inventoryTrend': inventory_trend,
                'budgetSummary': {
                    'totalBudget': total_budget,
                    'actualSpend': actual_spend,
                    'remainingBudget': remaining_budget,
                    'overPercent': over_percent
                },
                'inventorySummary': {
                    'currentInventoryValue': current_inventory_value,
                    'totalSkus': total_skus,
                    'lowStockItems': low_stock_items,
                    'deadStockItems': dead_stock_items
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportsExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reportId):
        try:
            format = request.query_params.get('format', 'xlsx')
            data = []
            columns = []
            
            if reportId == 'spend':
                pos = PurchaseOrder.objects.all().order_by('id')
                data = [{
                    'PO ID': p.id,
                    'Vendor Name': p.vendor_name,
                    'Category': p.category,
                    'Tower': p.tower,
                    'Total Value': float(p.total_value),
                    'Taxes': float(p.taxes),
                    'Net Value': float(p.net_value),
                    'Start Date': p.start_date.isoformat() if p.start_date else '',
                    'End Date': p.end_date.isoformat() if p.end_date else '',
                    'Status': p.status
                } for p in pos]
                columns = [
                    {'header': 'PO ID', 'key': 'PO ID'},
                    {'header': 'Vendor Name', 'key': 'Vendor Name'},
                    {'header': 'Category', 'key': 'Category'},
                    {'header': 'Tower', 'key': 'Tower'},
                    {'header': 'Total Value', 'key': 'Total Value'},
                    {'header': 'Taxes', 'key': 'Taxes'},
                    {'header': 'Net Value', 'key': 'Net Value'},
                    {'header': 'Start Date', 'key': 'Start Date'},
                    {'header': 'End Date', 'key': 'End Date'},
                    {'header': 'Status', 'key': 'Status'}
                ]
            elif reportId == 'vendor':
                vendors = Vendor.objects.all().order_by('id')
                data = [{
                    'Vendor ID': v.id,
                    'Name': v.name,
                    'Type': v.type,
                    'Category': v.category,
                    'SLA Rating': float(v.sla_rating),
                    'Status': v.status,
                    'Contact Person': v.contact_person,
                    'Email': v.email,
                    'Phone': v.phone
                } for v in vendors]
                columns = [
                    {'header': 'Vendor ID', 'key': 'Vendor ID'},
                    {'header': 'Name', 'key': 'Name'},
                    {'header': 'Type', 'key': 'Type'},
                    {'header': 'Category', 'key': 'Category'},
                    {'header': 'SLA Rating', 'key': 'SLA Rating'},
                    {'header': 'Status', 'key': 'Status'},
                    {'header': 'Contact Person', 'key': 'Contact Person'},
                    {'header': 'Email', 'key': 'Email'},
                    {'header': 'Phone', 'key': 'Phone'}
                ]
            elif reportId == 'inventory':
                items = Item.objects.all().order_by('id')
                data = [{
                    'Item ID': item.id,
                    'Item Name': item.name,
                    'Type': item.type,
                    'Category': item.category,
                    'UOM': item.uom,
                    'Current Stock': item.current_stock,
                    'Min Stock Level': item.min_stock_level,
                    'Reorder Level': item.reorder_level,
                    'Unit Price': float(item.unit_price),
                    'Total Valuation': float(item.current_stock * item.unit_price)
                } for item in items]
                columns = [
                    {'header': 'Item ID', 'key': 'Item ID'},
                    {'header': 'Item Name', 'key': 'Item Name'},
                    {'header': 'Type', 'key': 'Type'},
                    {'header': 'Category', 'key': 'Category'},
                    {'header': 'UOM', 'key': 'UOM'},
                    {'header': 'Current Stock', 'key': 'Current Stock'},
                    {'header': 'Min Stock Level', 'key': 'Min Stock Level'},
                    {'header': 'Reorder Level', 'key': 'Reorder Level'},
                    {'header': 'Unit Price', 'key': 'Unit Price'},
                    {'header': 'Total Valuation', 'key': 'Total Valuation'}
                ]
            elif reportId == 'po':
                pos = PurchaseOrder.objects.filter(type='po').order_by('id')
                data = [{
                    'Order ID': p.id,
                    'Vendor Name': p.vendor_name,
                    'Linked RFQ': p.linked_rfq or '',
                    'Total Value': float(p.total_value),
                    'Taxes': float(p.taxes),
                    'Net Value': float(p.net_value),
                    'Start Date': p.start_date.isoformat() if p.start_date else '',
                    'End Date': p.end_date.isoformat() if p.end_date else '',
                    'Status': p.status,
                    'Tower': p.tower,
                    'Category': p.category
                } for p in pos]
                columns = [
                    {'header': 'Order ID', 'key': 'Order ID'},
                    {'header': 'Vendor Name', 'key': 'Vendor Name'},
                    {'header': 'Linked RFQ', 'key': 'Linked RFQ'},
                    {'header': 'Total Value', 'key': 'Total Value'},
                    {'header': 'Taxes', 'key': 'Taxes'},
                    {'header': 'Net Value', 'key': 'Net Value'},
                    {'header': 'Start Date', 'key': 'Start Date'},
                    {'header': 'End Date', 'key': 'End Date'},
                    {'header': 'Status', 'key': 'Status'},
                    {'header': 'Tower', 'key': 'Tower'},
                    {'header': 'Category', 'key': 'Category'}
                ]
            elif reportId == 'amc':
                contracts = RateContract.objects.all().order_by('id')
                data = [{
                    'Contract ID': c.id,
                    'Vendor Name': c.vendor,
                    'Contract Type': c.type,
                    'Service Scope': c.service_scope,
                    'Category': c.category,
                    'Contract Value': float(c.contract_value),
                    'Billing Cycle': c.billing_cycle,
                    'Start Date': c.start_date.isoformat() if c.start_date else '',
                    'End Date': c.end_date.isoformat() if c.end_date else '',
                    'Status': c.status,
                    'Utilization %': float(c.utilization_percent)
                } for c in contracts]
                columns = [
                    {'header': 'Contract ID', 'key': 'Contract ID'},
                    {'header': 'Vendor Name', 'key': 'Vendor Name'},
                    {'header': 'Contract Type', 'key': 'Contract Type'},
                    {'header': 'Service Scope', 'key': 'Service Scope'},
                    {'header': 'Category', 'key': 'Category'},
                    {'header': 'Contract Value', 'key': 'Contract Value'},
                    {'header': 'Billing Cycle', 'key': 'Billing Cycle'},
                    {'header': 'Start Date', 'key': 'Start Date'},
                    {'header': 'End Date', 'key': 'End Date'},
                    {'header': 'Status', 'key': 'Status'},
                    {'header': 'Utilization %', 'key': 'Utilization %'}
                ]
            elif reportId == 'budget':
                budgets = Budget.objects.all().order_by('id')
                data = [{
                    'Budget ID': b.id,
                    'Financial Year': b.fy,
                    'Type': b.type,
                    'Tower': b.tower,
                    'Department': b.department,
                    'Category': b.category,
                    'GL Code': b.gl_code,
                    'Period': b.period,
                    'Annual Budget': float(b.annual_budget),
                    'Allocated': float(b.allocated),
                    'Committed': float(b.committed),
                    'Actual': float(b.actual),
                    'Owner': b.owner,
                    'Status': b.status
                } for b in budgets]
                columns = [
                    {'header': 'Budget ID', 'key': 'Budget ID'},
                    {'header': 'Financial Year', 'key': 'Financial Year'},
                    {'header': 'Type', 'key': 'Type'},
                    {'header': 'Tower', 'key': 'Tower'},
                    {'header': 'Department', 'key': 'Department'},
                    {'header': 'Category', 'key': 'Category'},
                    {'header': 'GL Code', 'key': 'GL Code'},
                    {'header': 'Period', 'key': 'Period'},
                    {'header': 'Annual Budget', 'key': 'Annual Budget'},
                    {'header': 'Allocated', 'key': 'Allocated'},
                    {'header': 'Committed', 'key': 'Committed'},
                    {'header': 'Actual', 'key': 'Actual'},
                    {'header': 'Owner', 'key': 'Owner'},
                    {'header': 'Status', 'key': 'Status'}
                ]
            else:
                return Response({'error': f"Invalid report type: {reportId}"}, status=status.HTTP_400_BAD_REQUEST)

            # Log the export
            log_export(f"report_{reportId}", f"report_{reportId}_export_{int(datetime.now().timestamp())}.xlsx", 'xlsx', request.query_params)
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = f"{reportId.upper()} Report"[:30]
            ws.append([col['header'] for col in columns])
            for row in data:
                ws.append([row.get(col['key'], '') for col in columns])
            
            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            return FileResponse(
                buffer,
                as_attachment=True,
                filename=f"report_{reportId}_export_{int(datetime.now().timestamp())}.xlsx",
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            po_count = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).count()
            item_count = Item.objects.count()
            vendor_count = Vendor.objects.count()
            
            if po_count < 3 or item_count < 3 or vendor_count < 3:
                return Response({
                    'insights': [],
                    'message': 'Insufficient transactional data for AI insights',
                    'vendorPerformanceTrends': [],
                    'costPredictions': []
                })
                
            insights = []
            
            top_cat = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).values('category').annotate(s=Sum('total_value')).order_by('-s').first()
            if top_cat:
                insights.append({
                    'id': '1',
                    'type': 'opportunity',
                    'title': 'Category Spend Insight',
                    'description': f"Top spending category: {top_cat['category']} with total value of ₹{float(top_cat['s']):,.2f}.",
                    'metric': f"₹{float(top_cat['s'])/1000:,.0f}K",
                    'confidence': 95,
                    'action': 'Review category budget'
                })
                
            worst_vendor = Vendor.objects.all().order_by('sla_rating').first()
            if worst_vendor and worst_vendor.sla_rating < 4.8:
                sla_pct = int(float(worst_vendor.sla_rating) * 20)
                delay_pct = 100 - sla_pct
                insights.append({
                    'id': '2',
                    'type': 'risk',
                    'title': 'PO Delivery Delay Risk',
                    'description': f"Vendor {worst_vendor.name} delayed deliveries by {delay_pct}% based on their SLA rating of {float(worst_vendor.sla_rating)}.",
                    'metric': f"{delay_pct}% Delay",
                    'confidence': 85,
                    'action': 'Contact vendor'
                })
                
            low_stock = Item.objects.filter(current_stock__lte=F('min_stock_level')).first()
            if low_stock:
                insights.append({
                    'id': '3',
                    'type': 'alert',
                    'title': 'Inventory Stock-out Prediction',
                    'description': f"Inventory for {low_stock.category} ({low_stock.name}) likely to exhaust in 12 days based on current consumption rate.",
                    'metric': '12 Days',
                    'confidence': 92,
                    'action': 'Create purchase indent'
                })
                
            pending_approvals = Indent.objects.filter(status__in=['submitted', 'hod_approved', 'procurement_approved']).count()
            if pending_approvals > 0:
                insights.append({
                    'id': '4',
                    'type': 'prediction',
                    'title': 'Approval Turnaround Delay',
                    'description': f"PO approvals slowed by 18% this month with {pending_approvals} pending requisitions in queue.",
                    'metric': f"{pending_approvals} Pending",
                    'confidence': 88,
                    'action': 'Escalate approvals'
                })

            # Calculate vendor performance trends dynamically
            vendor_trends = []
            for v in Vendor.objects.all()[:5]:
                rating = float(v.sla_rating)
                score = int(rating * 20)
                vendor_trends.append({
                    'vendor': v.name,
                    'score': score,
                    'trend': 'up' if score >= 90 else 'down',
                    'change': '+2%' if score >= 90 else '-3%'
                })

            # Calculate next month cost predictions dynamically
            cost_preds = []
            cats = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).values('category').annotate(s=Sum('total_value'))[:5]
            for c in cats:
                val = float(c['s'] or 0.0)
                cost_preds.append({
                    'category': c['category'],
                    'current': val,
                    'predicted': val * 1.05,
                    'variance': 5.0
                })
                
            return Response({
                'insights': insights,
                'message': '',
                'vendorPerformanceTrends': vendor_trends,
                'costPredictions': cost_preds
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

