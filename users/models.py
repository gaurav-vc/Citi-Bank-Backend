from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
import uuid


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('name', 'Admin')

        # REQUIRED FOR DJANGO ADMIN
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        unique=True
    )

    name = models.CharField(
        max_length=255
    )

    # unused field --> can be removed
    role = models.CharField(
        max_length=100,
        default='employee'
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    tower = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    force_password_change = models.BooleanField(
        default=False
    )

    # REQUIRED DJANGO AUTH FIELDS
    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    is_superuser = models.BooleanField(
        default=False
    )

    # REQUIRED FOR DJANGO AUTH SYSTEM
    last_login = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        db_column='user_id'
    )

    role_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='department_id'
    )

    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    profile_picture = models.TextField(
        blank=True,
        null=True
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='organization_id'
    )

    site = models.ForeignKey(
        'organizations.Site',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='site_id'
    )

    role = models.ForeignKey(
        'access_control.Role',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='role_id'
    )

    # Enriched fields
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    reporting_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='direct_reports'
    )
    access_scope = models.CharField(max_length=50, default='Department')
    is_active = models.BooleanField(default=True)
    last_login_site = models.ForeignKey(
        'organizations.Site',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='last_login_profiles'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if self.role:
            self.role_name = self.role.role_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} Profile"

    class Meta:
        db_table = 'user_profiles'
