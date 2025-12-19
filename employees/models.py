from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


class Department(models.Model):
    """Department model for organizational structure."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Designation(models.Model):
    """Designation/Job Title model."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='designations')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    """
    Extended User model for employees with additional fields.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('CT', 'Contract'),
        ('IN', 'Intern'),
    ]
    
    STATUS_CHOICES = [
        ('AC', 'Active'),
        ('IN', 'Inactive'),
        ('SU', 'Suspended'),
        ('TE', 'Terminated'),
    ]
    
    # Employee Information
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)
    
    # Employment Details
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    date_joined = models.DateTimeField(default=timezone.now)
    employment_type = models.CharField(
        max_length=2,
        choices=[
            ('FT', 'Full Time'),
            ('PT', 'Part Time'),
            ('CT', 'Contract'),
            ('IN', 'Intern'),
        ],
        default='FT'
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AC')
    
    # Biometric Information
    biometric_user_id = models.IntegerField(unique=True, null=True, blank=True, db_index=True,
                                           help_text="UID in biometric device")
    biometric_synced = models.BooleanField(default=False,
                                          help_text="Whether user is synced with biometric device")
    biometric_sync_date = models.DateTimeField(null=True, blank=True)
    
    # Leave Balance
    annual_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    sick_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    casual_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Return the full name of the employee."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def total_leave_balance(self):
        """Calculate total leave balance."""
        return self.annual_leave_balance + self.sick_leave_balance + self.casual_leave_balance
