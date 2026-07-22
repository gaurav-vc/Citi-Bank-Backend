from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile
from .serializers import UserSerializer, UserProfileSerializer


class MeView(APIView):
    """Return the authenticated user's current data with fresh permissions."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Auto-seed role permissions to ensure latest segregation mappings are active
            try:
                from procurement.management.commands.seed_roles import Command
                cmd = Command()
                cmd.stdout = type('DummyStdout', (object,), {'write': lambda *a, **k: None})()
                cmd.style = type('DummyStyle', (object,), {'SUCCESS': lambda *a, **k: a[0] if a else ''})()
                cmd.handle()
            except Exception as e:
                print("[AUTO-SEED ERROR]:", e)

            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email:
            email = email.strip()

        print(f"--- LOGIN ATTEMPT --- Email: '{email}', Password length: {len(password) if password else 0}")

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                print("LOGIN FAILED: User not found")
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.check_password(password):
                print("LOGIN FAILED: Incorrect password")
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                'token': str(refresh.access_token),
                'user': serializer.data,
                'force_password_change': user.force_password_change
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print("LOGIN EXCEPTION:", error_trace)
            return Response({'error': f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'employee')
        department = data.get('department')
        tower = data.get('tower')

        # Validation checks on target role
        if role in ('super_admin', 'client_admin', 'admin'):
            if not request.user or not request.user.is_authenticated:
                return Response({'error': 'Authentication required to create admin/staff roles.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            requester_role = request.user.role
            if role == 'super_admin' and requester_role != 'super_admin':
                return Response({'error': 'Only Super Admin can create Super Admins.'}, status=status.HTTP_403_FORBIDDEN)
            if role == 'client_admin' and requester_role != 'super_admin':
                return Response({'error': 'Only Super Admin can create Organization Admins.'}, status=status.HTTP_403_FORBIDDEN)
            if role == 'admin' and requester_role not in ('super_admin', 'client_admin', 'admin'):
                return Response({'error': 'Only Super Admin, Organization Admin, or Admin can create Admin users.'}, status=status.HTTP_403_FORBIDDEN)

        if not email or not name:
            return Response({'error': 'Missing required fields: email, name'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_409_CONFLICT)

        # Use default password if not provided
        if not password:
            password = "Demo@123"

        try:
            user = User.objects.create_user(
                email=email,
                name=name,
                role=role,
                department=department,
                tower=tower
            )
            print("PASSWORD USED:", password)
            user.set_password(password)
            user.force_password_change = False
            user.save()
            
            # Extract organization context from payload or inherit from authenticated requester
            org_id = data.get('organization_id') or data.get('organization')
            if not org_id and request.user and request.user.is_authenticated:
                requester_profile = getattr(request.user, 'profile', None)
                if requester_profile:
                    org_id = requester_profile.organization_id

            # Initialize profile
            profile = UserProfile.objects.create(user=user, role_name=role)
            if org_id:
                profile.organization_id = org_id
                profile.save()

            try:
                from utils.email_helper import send_employee_onboarding_email
                send_employee_onboarding_email(
                    email=email,
                    name=name,
                    password=password,
                    role=role
                )
            except Exception as email_err:
                print("ONBOARDING EMAIL ERROR:", str(email_err))

            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)

            return Response({
                'token': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("REGISTER ERROR:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role in ('client_admin', 'admin'):
            profile = getattr(user, 'profile', None)
            if profile and profile.organization_id:
                qs = qs.filter(organization_id=profile.organization_id)
        return qs

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        if not user_id:
            return Response({"error": "user field is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        profile = UserProfile.objects.filter(user_id=user_id).first()
        if profile:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return super().create(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'super_admin':
            org_id = self.request.query_params.get('organization_id')
            site_id = self.request.query_params.get('site_id')
            if org_id:
                qs = qs.filter(profile__organization_id=org_id)
            if site_id:
                qs = qs.filter(profile__site_id=site_id)
        elif user.role in ('client_admin', 'admin'):
            profile = getattr(user, 'profile', None)
            if profile:
                if profile.organization_id:
                    qs = qs.filter(profile__organization_id=profile.organization_id)
                if user.role == 'admin' and profile.site_id:
                    qs = qs.filter(profile__site_id=profile.site_id)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'employee')
        department_name = data.get('department')
        tower = data.get('tower')

        if not email or not name:
            return Response({'error': 'Missing required fields: email, name'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_409_CONFLICT)

        if not password:
            password = "Demo@123"

        user = User.objects.create_user(
            email=email,
            name=name,
            role=role,
            department=department_name,
            tower=tower
        )
        print("PASSWORD USED:", password)
        user.set_password(password)
        user.force_password_change = False
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role_name': role})
        
        org_id = data.get('organization_id') or data.get('organization')
        site_id = data.get('site_id') or data.get('site')
        
        if request.user and request.user.is_authenticated:
            requester_profile = getattr(request.user, 'profile', None)
            if request.user.role == 'admin':
                # Normal admin: ALWAYS force their own org and site — no overrides allowed
                org_id = requester_profile.organization_id if requester_profile else org_id
                site_id = requester_profile.site_id if requester_profile else site_id
            elif request.user.role != 'super_admin':
                # Other non-super-admin roles: inherit org if not specified
                if requester_profile:
                    org_id = org_id or requester_profile.organization_id
        
        if org_id:
            profile.organization_id = org_id

        if site_id:
            profile.site_id = site_id
            
        profile.department_id = data.get('department_id') or data.get('department')
        profile.employee_id = data.get('employee_id')
        profile.designation = data.get('designation')
        profile.phone_number = data.get('phone_number') or data.get('mobile')
        profile.access_scope = data.get('access_scope', 'Department')
        profile.is_active = data.get('is_active', True)
        
        reporting_manager_id = data.get('reporting_manager') or data.get('reporting_manager_id')
        if reporting_manager_id:
            profile.reporting_manager_id = reporting_manager_id
            
        profile.save()

        try:
            from utils.email_helper import send_employee_onboarding_email
            send_employee_onboarding_email(
                email=email,
                name=name,
                password=password,
                role=role
            )
        except Exception as email_err:
            print("ONBOARDING EMAIL ERROR:", str(email_err))

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # get_object respects get_queryset scope — admin can't touch other sites
        data = request.data

        if 'email' in data:
            instance.email = data['email']
        if 'name' in data:
            instance.name = data['name']
        if 'role' in data:
            instance.role = data['role']
        if 'department' in data:
            instance.department = data['department']
        if 'tower' in data:
            instance.tower = data['tower']
        if 'is_active' in data:
            instance.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            instance.set_password(data['password'])
            
        instance.save()

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        
        if 'role' in data:
            profile.role_name = data['role']
            from access_control.models import Role as DBRole
            db_role = DBRole.objects.filter(role_name=data['role']).first()
            if db_role:
                profile.role = db_role

        # For admin users: never allow changing org_id or site_id
        if request.user.role == 'super_admin':
            if 'organization_id' in data or 'organization' in data:
                profile.organization_id = data.get('organization_id') or data.get('organization')
            if 'site_id' in data or 'site' in data:
                profile.site_id = data.get('site_id') or data.get('site')
        # else: org/site stays unchanged for admin users

        if 'department_id' in data or 'department' in data:
            profile.department_id = data.get('department_id') or data.get('department')
        if 'employee_id' in data:
            profile.employee_id = data['employee_id']
        if 'designation' in data:
            profile.designation = data['designation']
        if 'mobile' in data or 'phone_number' in data:
            profile.phone_number = data.get('phone_number') or data.get('mobile')
        if 'access_scope' in data:
            profile.access_scope = data['access_scope']
        if 'is_active' in data:
            profile.is_active = data['is_active']
        if 'reporting_manager' in data or 'reporting_manager_id' in data:
            profile.reporting_manager_id = data.get('reporting_manager') or data.get('reporting_manager_id')

        profile.save()

        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        qs = self.get_queryset().filter(is_active=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        profile = getattr(user, 'profile', None)
        if profile:
            profile.is_active = True
            profile.save()
        return Response({"success": True, "message": "User approved successfully"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({"success": True, "message": "User rejected successfully"})



class CompatibilityAssignUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('userId') or request.data.get('user_id')
        organization_id = request.data.get('organizationId') or request.data.get('organization_id')
        site_id = request.data.get('siteId') or request.data.get('site_id')
        department_id = request.data.get('departmentId') or request.data.get('department_id')
        role_name = request.data.get('role') or request.data.get('role_name')
        requester_role = request.user.role

        try:
            user = User.objects.get(id=user_id)
            
            # If the user being modified is a super_admin or client_admin, only a super_admin can modify them
            if user.role == 'super_admin' and requester_role != 'super_admin':
                return Response({'error': 'Only Super Admin can modify a Super Admin user.'}, status=status.HTTP_403_FORBIDDEN)
            if user.role == 'client_admin' and requester_role != 'super_admin':
                return Response({'error': 'Only Super Admin can modify an Organization Admin.'}, status=status.HTTP_403_FORBIDDEN)

            if role_name:
                if role_name == 'super_admin' and requester_role != 'super_admin':
                    return Response({'error': 'Only Super Admin can assign the Super Admin role.'}, status=status.HTTP_403_FORBIDDEN)
                if role_name == 'client_admin' and requester_role != 'super_admin':
                    return Response({'error': 'Only Super Admin can assign the Organization Admin role.'}, status=status.HTTP_403_FORBIDDEN)
                if role_name == 'admin' and requester_role not in ('super_admin', 'client_admin', 'admin'):
                    return Response({'error': 'Only Super Admin, Organization Admin, or Admin can assign the Admin role.'}, status=status.HTTP_403_FORBIDDEN)
                
                user.role = role_name
                user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.organization_id = organization_id
            profile.site_id = site_id
            profile.department_id = department_id
            if role_name:
                profile.role_name = role_name
            profile.save()

            return Response({
                "success": True,
                "message": "User assigned successfully"
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordFirstLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)

        if current_password:
            if not user.check_password(current_password):
                return Response({'error': 'Incorrect current password'}, status=status.HTTP_400_BAD_REQUEST)

        print("PASSWORD USED:", new_password)
        user.set_password(new_password)
        user.force_password_change = False
        user.save()

        # Update onboarding status on Vendor side
        from vendors.models import Vendor, AuditLog
        vendor = Vendor.objects.filter(email=user.email).first()
        if vendor:
            vendor.onboarding_status = 'Active'
            vendor.save()
            AuditLog.objects.create(
                action='First Login Completed',
                target_type='vendor',
                target_id=vendor.id,
                actioned_by=user.email,
                comments='First login password change successfully completed.'
            )
        else:
            AuditLog.objects.create(
                action='Password Reset Completed',
                target_type='user',
                target_id=str(user.id),
                actioned_by=user.email,
                comments='Password change completed successfully.'
            )

        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'message': 'Password changed successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
