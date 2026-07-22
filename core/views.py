from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Avg
from procurement.models import PurchaseOrder, Budget, Indent, Invoice
from vendors.models import Vendor, RateContract
from inventory.models import Item
import re

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 1. Total Spend
            total_spend_val = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).aggregate(value=Sum('net_value'))['value'] or 0.00
            total_spend = float(total_spend_val)

            # 2. Budget Utilization
            budget_agg = Budget.objects.aggregate(actual=Sum('actual'), budget=Sum('annual_budget'))
            actual_budget = float(budget_agg['actual'] or 0)
            annual_budget = float(budget_agg['budget'] or 0)
            budget_utilization = round((actual_budget / annual_budget) * 100) if annual_budget > 0 else 0

            # 3. Open POs
            open_pos = PurchaseOrder.objects.filter(status__in=['pending', 'pending_procurement_approval', 'approved', 'active', 'budget_hold']).count()

            # 4. Pending Approvals
            from workflows.models import WorkflowStep
            pending_approvals = WorkflowStep.objects.filter(assigned_role_name=request.user.role, status='pending').count()

            # 5. Inventory Value
            items = Item.objects.all()
            inventory_value = sum(float(i.current_stock) * float(i.unit_price) for i in items)

            # 6. Outstanding Payments
            outstanding_payments_val = Invoice.objects.filter(status__in=['pending_approval', 'approved']).aggregate(value=Sum('total_amount'))['value'] or 0.00
            outstanding_payments = float(outstanding_payments_val)

            # 7. Vendor Compliance
            avg_rating = Vendor.objects.aggregate(value=Avg('sla_rating'))['value'] or 0.00
            vendor_compliance = round(float(avg_rating) * 20)

            # 8. AMC Renewals
            amc_renewals = RateContract.objects.filter(status='expiring_soon').count()

            metrics = {
                "totalSpend": {"value": total_spend, "previousValue": total_spend * 0.9, "trend": "up"},
                "budgetUtilization": {"value": budget_utilization, "previousValue": 68, "trend": "up"},
                "openPOs": {"value": open_pos, "previousValue": open_pos + 4, "trend": "down"},
                "pendingApprovals": {"value": pending_approvals, "previousValue": pending_approvals + 2, "trend": "down"},
                "inventoryValue": {"value": inventory_value, "previousValue": inventory_value * 0.95, "trend": "up"},
                "outstandingPayments": {"value": outstanding_payments, "previousValue": outstanding_payments * 0.9, "trend": "up"},
                "vendorCompliance": {"value": vendor_compliance, "previousValue": 91, "trend": "up"},
                "amcRenewals": {"value": amc_renewals, "previousValue": 3, "trend": "up"}
            }

            # 9. Monthly Spend Trend
            pos = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).order_by('start_date')
            monthly_map = {}
            for p in pos:
                month_str = p.start_date.strftime('%b')
                monthly_map[month_str] = monthly_map.get(month_str, 0) + float(p.net_value)
            
            monthly_spend_data = [{"month": m, "spend": val} for m, val in monthly_map.items()]
            monthly_spend = [{"month": m, "value": val} for m, val in monthly_map.items()]
            # 10. Category Spend
            categories = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).values('category').annotate(value=Sum('net_value')).order_by('-value')
            colors = [
                'hsl(173, 58%, 39%)',
                'hsl(222, 47%, 30%)',
                'hsl(38, 92%, 50%)',
                'hsl(142, 71%, 45%)',
                'hsl(215, 16%, 47%)',
                'hsl(262, 83%, 58%)'
            ]
            category_spend = []
            category_spend_list = []
            for i, c in enumerate(categories):
                category_name = c['category'] or 'Other'
                category_spend.append({
                    "name": category_name,
                    "value": float(c['value'] or 0),
                    "color": colors[i % len(colors)]
                })
                category_spend_list.append({
                    "category": category_name,
                    "value": float(c['value'] or 0)
                })

            # 11. Drilldown Analysis
            pos_drill = PurchaseOrder.objects.filter(status__in=['approved', 'active', 'completed']).values('tower', 'category', 'vendor_name').annotate(spend=Sum('net_value'))
            towers_map = {}
            for r in pos_drill:
                tower_name = r['tower'] or 'Tower A'
                cat_name = r['category']
                vendor_name = r['vendor_name']
                amount = float(r['spend'] or 0)

                if tower_name not in towers_map:
                    towers_map[tower_name] = {"id": tower_name.lower().replace(' ', '-'), "label": tower_name, "value": 0, "categories": {}}
                towers_map[tower_name]["value"] += amount

                if cat_name not in towers_map[tower_name]["categories"]:
                    towers_map[tower_name]["categories"][cat_name] = {"id": f"{towers_map[tower_name]['id']}-{cat_name.lower()}", "label": cat_name, "value": 0, "vendors": {}}
                towers_map[tower_name]["categories"][cat_name]["value"] += amount

                if vendor_name not in towers_map[tower_name]["categories"][cat_name]["vendors"]:
                    clean_vendor = re.sub(r'[^a-z0-9]', '', vendor_name.lower())
                    towers_map[tower_name]["categories"][cat_name]["vendors"][vendor_name] = {"id": f"{towers_map[tower_name]['categories'][cat_name]['id']}-{clean_vendor}", "label": vendor_name, "value": 0}
                towers_map[tower_name]["categories"][cat_name]["vendors"][vendor_name]["value"] += amount

            total_spend_drilldown = []
            for t_name, t in towers_map.items():
                children = []
                for c_name, c in t['categories'].items():
                    v_children = [{"id": v['id'], "label": v_name, "value": v['value']} for v_name, v in c['vendors'].items()]
                    children.append({"id": c['id'], "label": c_name, "value": c['value'], "children": v_children})
                total_spend_drilldown.append({"id": t['id'], "label": t_name, "value": t['value'], "children": children})

            return Response({
                "dashboardMetrics": metrics,
                "monthlySpendData": monthly_spend_data,
                "categorySpend": category_spend,
                "monthly_spend": monthly_spend,
                "category_spend": category_spend_list,
                "totalSpendDrilldown": total_spend_drilldown
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
