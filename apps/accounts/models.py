from django.db import models
import arrow
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as t
from apps.accounts.utils import send_login_credentials
import uuid


# Create your models here.
class UserRole(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', t('Admin'),
        STAFF = 'staff', t('Staff'),
        CUSTOMER = 'customer', t('Customer')
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, choices=Role.choices, default=Role.CUSTOMER, verbose_name=t("User's Role"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=t("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=t("Updated at"))
    
    class Meta:
        verbose_name = t("User Role")
        verbose_name_plural = t("User Roles")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f'{self.name}'
    

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, null= True, blank=True, verbose_name=t("Username"))
    profile = models.ImageField(null=True, blank=True, upload_to="profiles")
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    password = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        related_name='user_role',
        null=True,
        blank=True,
    )
    phone_number = models.IntegerField(null=True, blank=True)
    login_enabled = models.BooleanField(default=True)
    password_changed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=t("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=t("Updated at"))
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        swappable = 'AUTH_USER_MODEL'
    
    def __str__(self):
        return self.username
    
    def generate_temporal_password(self):
        passw= uuid.uuid4().hex[:8]
        hashed_password = make_password(passw)
        send_login_credentials(self.email, passw, self.phone_number)
        return hashed_password
    
    def save(self,*args, **kwargs):
        if not self.username and self.email:
            self.username = self.email.split('@')[0].strip()
        
        if not self.password:
            self.password = self.generate_temporal_password()
            self.password_expiry = arrow.now().shift(days=+3).datetime
            self.login_enabled = False
        
        super().save(*args, **kwargs)
    
    def is_password_expired(self):
        return arrow.now() > arrow.get(self.password_expiry)
    
    
    
class StaffProfile(models.Model):
    STAFF_ROLES = [
        ('Manager', "Manager"),
        ('Receptionist', 'Receptionist'),
        ('Bartender', "Bartender"),
        ('Waiter', "Waiter"),
        ('Housekeeper', "Housekeeper"),
        ('Security', "Security"),
    ]
    HIGHEST_EDUCATION_LEVEL = [
        ('High School', "High School"),
        ('Diploma', "Diploma"),
        ('Bachelor', "Bachelor"),
        ('Master', "Master"),
        ('Certification', "Certification"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff')
    profile = models.ImageField(null=True, blank=True, upload_to="profiles")
    staff_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    highest_education_level = models.CharField(max_length=255, choices=HIGHEST_EDUCATION_LEVEL, null=True, blank=True)
    staff_role = models.CharField(max_length=255, choices=STAFF_ROLES, null=True)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=20, decimal_places=5, null=False)
    emergency_contact = models.CharField(max_length=255, null=True, blank=True)
    is_on_duty = models.BooleanField(default=False)



class CustomerProfile(models.Model):
    CUSTOMER_STATUS = [
        ('Loyalty', 'Loyalty'),
        ('Guest', 'Guest'),
    ]
    PREFERRED_PAYMENT_METHOD=[
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Mobile-Money', 'Mobile-Money'),
    ]
    ID_PROOF_TYPE = [
        ('National ID', 'National ID'),
        ('Passport', 'Passport'),
        ('Drivers License', 'Drivers License'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    profile = models.ImageField(null=True, blank=True, upload_to="profiles")
    customer_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_status = models.CharField(max_length=255, choices=CUSTOMER_STATUS, null=True)
    preffered_payment_method = models.CharField(max_length=255, choices=PREFERRED_PAYMENT_METHOD, null=False)
    loyalty_points = models.IntegerField(default=0)
    special_requests = models.TextField(null=True, blank=True)
    id_proof_type = models.CharField(max_length=255, choices=ID_PROOF_TYPE, null=True)
    id_proof_number = models.CharField(max_length=255, null=True)
    verified = models.BooleanField(default=False)
    
class Branch(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    image = models.ImageField(upload_to='branches', null=True,blank=True)
    name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    manager = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = t("Branch")
        verbose_name_plural = t("Branches")
        ordering = ['-created_at']
    