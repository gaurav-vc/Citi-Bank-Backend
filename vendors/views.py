from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.http import HttpResponse, FileResponse
from datetime import datetime, date
import json
from io import BytesIO
import openpyxl
from access_control.permissions import RBACPermission
from .models import Vendor, RateContract
from .serializers import VendorSerializer, RateContractSerializer
from utils.exporter import export_data
from utils.importer import parse_uploaded_file
from utils.db_logger import log_export, log_import_start, log_import_failed_row, log_import_end

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_queryset(self):
        queryset = Vendor.objects.all()
        category = self.request.query_params.get('category')
        if category:
            from django.db.models import Q
            queryset = queryset.filter(Q(category__iexact=category) | Q(is_universal_vendor=True))
        return queryset

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        gst_number = request.data.get('gst_number')
        pan = request.data.get('pan')
        name = request.data.get('name')

        if not email or not name:
            return Response({'error': 'Name and Email are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        from rest_framework.exceptions import ValidationError
        errors = {}
        if Vendor.objects.filter(email=email).exists():
            errors['email'] = 'A vendor with this email already exists.'
        if gst_number and Vendor.objects.filter(gst_number=gst_number).exists():
            errors['gst_number'] = 'A vendor with this GST number already exists.'
        if pan and Vendor.objects.filter(pan=pan).exists():
            errors['pan'] = 'A vendor with this PAN number already exists.'
            
        if errors:
            raise ValidationError(errors)

        with transaction.atomic():
            vendor_id = request.data.get('id') or f"V{int(datetime.now().timestamp())}"
            
            temp_password = "Demo@123"

            from users.models import User, UserProfile
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(
                    email=email,
                    name=name,
                    role='vendor',
                    force_password_change=False,
                    is_active=True
                )
                print("PASSWORD USED:", temp_password)
                user.set_password(temp_password)
                user.force_password_change = False
                user.save()
                
                profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role_name': 'vendor'})
                profile.is_active = True
                profile.save()

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            vendor = serializer.save(id=vendor_id, user_id=str(user.id), onboarding_status='Account Created')

            from .models import AuditLog
            AuditLog.objects.create(
                action='Vendor Created',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Vendor '{vendor.name}' auto-created and linked to user account."
            )

        email_warning = None
        try:
            from utils.email_helper import send_vendor_onboarding_email
            send_vendor_onboarding_email(email=email, name=name, temp_password=temp_password)
            vendor.onboarding_status = 'Email Sent'
            vendor.save()
            
            AuditLog.objects.create(
                action='Credentials Sent',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Onboarding email sent to {email}."
            )
        except Exception as e:
            email_warning = f"Vendor created successfully, but credential email could not be delivered."
            print("VENDOR EMAIL FAILURE:", str(e))
            
            AuditLog.objects.create(
                action='Credentials Send Failed',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Onboarding email delivery failed: {str(e)}."
            )

        response_serializer = self.get_serializer(vendor)
        response_data = response_serializer.data
        if email_warning:
            return Response({
                'warning': email_warning,
                'vendor': response_data
            }, status=status.HTTP_201_CREATED)
            
        return Response(response_data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        instance = self.get_object()
        gst_number = self.request.data.get('gst_number')
        pan = self.request.data.get('pan')
        email = self.request.data.get('email')

        from rest_framework.exceptions import ValidationError
        errors = {}
        if email and Vendor.objects.filter(email=email).exclude(id=instance.id).exists():
            errors['email'] = 'A vendor with this email already exists.'
        if gst_number and Vendor.objects.filter(gst_number=gst_number).exclude(id=instance.id).exists():
            errors['gst_number'] = 'A vendor with this GST number already exists.'
        if pan and Vendor.objects.filter(pan=pan).exclude(id=instance.id).exists():
            errors['pan'] = 'A vendor with this PAN number already exists.'
            
        if errors:
            raise ValidationError(errors)

        vendor = serializer.save()
        
        from .models import AuditLog
        AuditLog.objects.create(
            action='Vendor Updated',
            target_type='vendor',
            target_id=vendor.id,
            actioned_by=self.request.user.email,
            comments=f"Vendor details updated."
        )

    @action(detail=True, methods=['post'], url_path='resend-credentials')
    def resend_credentials(self, request, pk=None):
        vendor = self.get_object()
        
        from users.models import User
        user = User.objects.filter(email=vendor.email).first()
        if not user:
            temp_password = "Demo@123"
            user = User.objects.create_user(
                email=vendor.email,
                name=vendor.name,
                role='vendor',
                force_password_change=False,
                is_active=vendor.status == 'active'
            )
            print("PASSWORD USED:", temp_password)
            user.set_password(temp_password)
            user.force_password_change = False
            user.save()
        else:
            temp_password = "Demo@123"
            print("PASSWORD USED:", temp_password)
            user.set_password(temp_password)
            user.force_password_change = False
            user.save()

        try:
            from utils.email_helper import send_vendor_onboarding_email
            send_vendor_onboarding_email(email=vendor.email, name=vendor.name, temp_password=temp_password)
            vendor.onboarding_status = 'Email Sent'
            vendor.save()
            
            from .models import AuditLog
            AuditLog.objects.create(
                action='Password Reset Triggered',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Password reset triggered as part of resending credentials."
            )
            AuditLog.objects.create(
                action='Credentials Resent',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Credentials resent successfully to {vendor.email}."
            )
            return Response({"success": True, "message": "Credentials resent successfully"})
        except Exception as e:
            from .models import AuditLog
            AuditLog.objects.create(
                action='Credentials Resend Failed',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Failed to resend credentials: {str(e)}"
            )
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        vendor = self.get_object()
        from users.models import User
        user = User.objects.filter(email=vendor.email).first()
        if not user:
            return Response({"error": "No user account linked to this vendor"}, status=status.HTTP_404_NOT_FOUND)

        temp_password = "Demo@123"

        print("PASSWORD USED:", temp_password)
        user.set_password(temp_password)
        user.force_password_change = False
        user.save()

        vendor.onboarding_status = 'First Login Pending'
        vendor.save()

        try:
            from utils.email_helper import send_vendor_onboarding_email
            send_vendor_onboarding_email(email=vendor.email, name=vendor.name, temp_password=temp_password)
            
            from .models import AuditLog
            AuditLog.objects.create(
                action='Password Reset Triggered',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Password reset triggered by admin. Temporary credentials emailed."
            )
            return Response({"success": True, "message": "Password reset successfully and credentials emailed."})
        except Exception as e:
            from .models import AuditLog
            AuditLog.objects.create(
                action='Password Reset Failed',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=request.user.email,
                comments=f"Password reset succeeded but email failed to send: {str(e)}"
            )
            return Response({"warning": f"Password reset succeeded, but credentials email delivery failed: {str(e)}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        vendor = self.get_object()
        new_status = 'inactive' if vendor.status == 'active' else 'active'
        vendor.status = new_status
        vendor.save()

        from users.models import User
        user = User.objects.filter(email=vendor.email).first()
        if user:
            user.is_active = (new_status == 'active')
            user.save()

        action_name = 'Vendor Disabled' if new_status == 'inactive' else 'Vendor Activated'
        from .models import AuditLog
        AuditLog.objects.create(
            action=action_name,
            target_type='vendor',
            target_id=vendor.id,
            actioned_by=request.user.email,
            comments=f"Vendor status changed to '{new_status}'."
        )

        return Response({
            "success": True, 
            "status": new_status, 
            "message": f"Vendor successfully {'disabled' if new_status == 'inactive' else 'activated'}."
        })

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        try:
            format = request.query_params.get('format', 'xlsx')
            vendors = Vendor.objects.all().order_by('id')
            data = [{
                'id': v.id,
                'name': v.name,
                'type': v.type,
                'category': v.category,
                'gst_number': v.gst_number,
                'pan': v.pan,
                'msme_status': 'Yes' if v.msme_status else 'No',
                'bank_name': v.bank_name,
                'account_number': v.account_number,
                'ifsc': v.ifsc,
                'sla_rating': float(v.sla_rating),
                'approved_towers': ", ".join(v.approved_towers) if isinstance(v.approved_towers, list) else str(v.approved_towers),
                'compliance_expiry': v.compliance_expiry.isoformat() if isinstance(v.compliance_expiry, (date, datetime)) else str(v.compliance_expiry),
                'status': v.status,
                'contact_person': v.contact_person,
                'email': v.email,
                'phone': v.phone
            } for v in vendors]

            columns = [
                {'header': 'Vendor ID', 'key': 'id'},
                {'header': 'Name', 'key': 'name'},
                {'header': 'Type', 'key': 'type'},
                {'header': 'Category', 'key': 'category'},
                {'header': 'GST Number', 'key': 'gst_number'},
                {'header': 'PAN', 'key': 'pan'},
                {'header': 'MSME Registered', 'key': 'msme_status'},
                {'header': 'Bank Name', 'key': 'bank_name'},
                {'header': 'Account Number', 'key': 'account_number'},
                {'header': 'IFSC Code', 'key': 'ifsc'},
                {'header': 'SLA Rating', 'key': 'sla_rating'},
                {'header': 'Approved Towers', 'key': 'approved_towers'},
                {'header': 'Compliance Expiry', 'key': 'compliance_expiry'},
                {'header': 'Status', 'key': 'status'},
                {'header': 'Contact Person', 'key': 'contact_person'},
                {'header': 'Email', 'key': 'email'},
                {'header': 'Phone', 'key': 'phone'}
            ]

            log_export('vendors', f"vendors_export_{int(datetime.now().timestamp())}.xlsx", 'xlsx', request.query_params)
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Vendors"
            ws.append([col['header'] for col in columns])
            for row in data:
                ws.append([row.get(col['key'], '') for col in columns])
            
            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            return FileResponse(
                buffer,
                as_attachment=True,
                filename=f"vendors_export_{int(datetime.now().timestamp())}.xlsx",
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='import')
    def import_vendors(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = parse_uploaded_file(uploaded_file)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        file_type = uploaded_file.name.split('.')[-1].lower()
        log_id = log_import_start('vendors', uploaded_file.name, file_type, len(rows))

        validation_errors = []
        valid_rows = []

        for idx, row in enumerate(rows):
            row_idx = idx + 1
            row_errors = []

            v_id = row.get('id')
            if not v_id:
                row_errors.append("Missing Vendor ID")
            v_name = row.get('name')
            if not v_name:
                row_errors.append("Missing Name")
            v_type = row.get('type')
            if not v_type:
                row_errors.append("Missing Type")
            v_cat = row.get('category')
            if not v_cat:
                row_errors.append("Missing Category")
            v_email = row.get('email')
            if not v_email:
                row_errors.append("Missing Email")

            if row_errors:
                err_msg = "; ".join(row_errors)
                validation_errors.append(f"Row {row_idx}: {err_msg}")
                log_import_failed_row(log_id, row_idx, row, err_msg)
            else:
                valid_rows.append((row, row_idx))

        if validation_errors:
            log_import_end(log_id, 'failed', 0, len(rows))
            return Response({
                'error': 'Import failed validation',
                'errors': validation_errors,
                'totalRows': len(rows),
                'processedRows': 0,
                'failedRows': len(rows)
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            with transaction.atomic():
                for row, row_idx in valid_rows:
                    # Parse msme
                    msme_val = str(row.get('msme_status', 'No')).strip().lower()
                    msme_status = msme_val in ('yes', 'true', '1')
                    
                    # Parse approved towers list
                    towers_str = row.get('approved_towers', '[]')
                    if towers_str.startswith('[') and towers_str.endswith(']'):
                        try:
                            approved_towers = json.loads(towers_str.replace("'", '"'))
                        except Exception:
                            approved_towers = [t.strip() for t in towers_str[1:-1].split(',') if t.strip()]
                    else:
                        approved_towers = [t.strip() for t in towers_str.split(',') if t.strip()]

                    # Compliance expiry date
                    exp_val = row.get('compliance_expiry', '2027-12-31')
                    try:
                        compliance_expiry = datetime.strptime(exp_val[:10], '%Y-%m-%d').date()
                    except Exception:
                        compliance_expiry = date(2027, 12, 31)

                    Vendor.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'name': row['name'],
                            'type': row['type'],
                            'category': row['category'],
                            'gst_number': row.get('gst_number', ''),
                            'pan': row.get('pan', ''),
                            'msme_status': msme_status,
                            'bank_name': row.get('bank_name', 'HDFC Bank'),
                            'account_number': row.get('account_number', ''),
                            'ifsc': row.get('ifsc', ''),
                            'sla_rating': float(row.get('sla_rating', '4.5')),
                            'approved_towers': approved_towers,
                            'compliance_expiry': compliance_expiry,
                            'status': row.get('status', 'active'),
                            'contact_person': row.get('contact_person', 'Contact'),
                            'email': row['email'],
                            'phone': row.get('phone', '')
                        }
                    )

            log_import_end(log_id, 'success', len(valid_rows), 0)
            return Response({
                'success': True,
                'message': f"Successfully imported {len(valid_rows)} vendors",
                'totalRows': len(rows),
                'processedRows': len(valid_rows),
                'failedRows': 0
            }, status=status.HTTP_200_OK)

        except Exception as e:
            log_import_end(log_id, 'failed', 0, len(rows))
            return Response({'error': f"Vendor import error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RateContractViewSet(viewsets.ModelViewSet):
    queryset = RateContract.objects.all()
    serializer_class = RateContractSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        try:
            format = request.query_params.get('format', 'xlsx')
            contracts = RateContract.objects.all().order_by('id')
            data = [{
                'id': c.id,
                'vendor': c.vendor,
                'vendor_id': c.vendor_id,
                'type': c.type,
                'service_scope': c.service_scope,
                'category': c.category,
                'contract_value': float(c.contract_value),
                'billing_cycle': c.billing_cycle,
                'start_date': c.start_date.isoformat() if isinstance(c.start_date, (date, datetime)) else str(c.start_date),
                'end_date': c.end_date.isoformat() if isinstance(c.end_date, (date, datetime)) else str(c.end_date),
                'sla_kpis': json.dumps(c.sla_kpis) if isinstance(c.sla_kpis, list) else str(c.sla_kpis),
                'status': c.status,
                'utilization_percent': float(c.utilization_percent),
                'last_billing_date': c.last_billing_date.isoformat() if isinstance(c.last_billing_date, (date, datetime)) else (str(c.last_billing_date) if c.last_billing_date else ''),
                'next_billing_date': c.next_billing_date.isoformat() if isinstance(c.next_billing_date, (date, datetime)) else (str(c.next_billing_date) if c.next_billing_date else ''),
            } for c in contracts]

            columns = [
                {'header': 'Contract ID', 'key': 'id'},
                {'header': 'Vendor', 'key': 'vendor'},
                {'header': 'Vendor ID', 'key': 'vendor_id'},
                {'header': 'Type', 'key': 'type'},
                {'header': 'Service Scope', 'key': 'service_scope'},
                {'header': 'Category', 'key': 'category'},
                {'header': 'Contract Value', 'key': 'contract_value'},
                {'header': 'Billing Cycle', 'key': 'billing_cycle'},
                {'header': 'Start Date', 'key': 'start_date'},
                {'header': 'End Date', 'key': 'end_date'},
                {'header': 'SLA KPIs', 'key': 'sla_kpis'},
                {'header': 'Status', 'key': 'status'},
                {'header': 'Utilization Percent', 'key': 'utilization_percent'},
                {'header': 'Last Billing Date', 'key': 'last_billing_date'},
                {'header': 'Next Billing Date', 'key': 'next_billing_date'},
            ]

            log_export('rate_contracts', f"contracts_export_{int(datetime.now().timestamp())}.xlsx", 'xlsx', request.query_params)
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Rate Contracts"
            ws.append([col['header'] for col in columns])
            for row in data:
                ws.append([row.get(col['key'], '') for col in columns])
            
            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            return FileResponse(
                buffer,
                as_attachment=True,
                filename=f"contracts_export_{int(datetime.now().timestamp())}.xlsx",
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='import')
    def import_contracts(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = parse_uploaded_file(uploaded_file)
            imported_count = 0
            errors = []

            for idx, row in enumerate(rows):
                row_idx = idx + 2
                try:
                    c_id = row.get('id') or row.get('contract_id') or row.get('contract_number')
                    if not c_id:
                        errors.append(f"Row {row_idx}: Missing Contract ID/Number")
                        continue

                    vendor = row.get('vendor') or ''
                    vendor_id = row.get('vendor_id') or ''
                    c_type = row.get('type') or 'amc'
                    service_scope = row.get('service_scope') or ''
                    category = row.get('category') or ''
                    
                    try:
                        contract_value = float(row.get('contract_value') or 0)
                    except ValueError:
                        contract_value = 0.0
                        
                    billing_cycle = row.get('billing_cycle') or 'quarterly'
                    
                    def parse_date(date_str):
                        if not date_str:
                            return None
                        try:
                            return datetime.strptime(date_str[:10], '%Y-%m-%d').date()
                        except Exception:
                            return None

                    start_date = parse_date(row.get('start_date')) or date.today()
                    end_date = parse_date(row.get('end_date')) or date.today()
                    
                    sla_kpis_str = row.get('sla_kpis', '[]')
                    try:
                        sla_kpis = json.loads(sla_kpis_str.replace("'", '"'))
                    except Exception:
                        sla_kpis = [k.strip() for k in sla_kpis_str.split(',') if k.strip()]

                    status_val = row.get('status') or 'active'
                    
                    try:
                        utilization_percent = float(row.get('utilization_percent') or 0)
                    except ValueError:
                        utilization_percent = 0.0
                        
                    last_billing_date = parse_date(row.get('last_billing_date'))
                    next_billing_date = parse_date(row.get('next_billing_date'))

                    RateContract.objects.update_or_create(
                        id=c_id,
                        defaults={
                            'vendor': vendor,
                            'vendor_id': vendor_id,
                            'type': c_type,
                            'service_scope': service_scope,
                            'category': category,
                            'contract_value': contract_value,
                            'billing_cycle': billing_cycle,
                            'start_date': start_date,
                            'end_date': end_date,
                            'sla_kpis': sla_kpis,
                            'status': status_val,
                            'utilization_percent': utilization_percent,
                            'last_billing_date': last_billing_date,
                            'next_billing_date': next_billing_date,
                        }
                    )
                    imported_count += 1
                except Exception as row_err:
                    errors.append(f"Row {row_idx}: {str(row_err)}")

            return Response({"imported": imported_count, "errors": errors}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
