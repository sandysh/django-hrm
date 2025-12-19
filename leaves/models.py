from django.db import models
from employees.models import Employee


class LeaveType(models.Model):
    """
    Different types of leaves available.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    default_days = models.IntegerField(default=0, help_text="Default number of days per year")
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LeaveRequest(models.Model):
    """
    Leave requests submitted by employees.
    """
    STATUS_CHOICES = [
        ('PE', 'Pending'),
        ('AP', 'Approved'),
        ('RJ', 'Rejected'),
        ('CA', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='leave_requests')
    
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2,
                                    help_text="Total number of leave days")
    
    reason = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PE')
    
    # Approval information
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # Attachments
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        # Calculate total days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
        super().save(*args, **kwargs)


class Holiday(models.Model):
    """
    Public holidays.
    """
    name = models.CharField(max_length=200)
    date = models.DateField(unique=True)
    description = models.TextField(blank=True)
    is_optional = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holidays'
        ordering = ['date']
    
    def __str__(self):
        return f"{self.name} - {self.date}"


class LeaveBalance(models.Model):
    """
    Track leave balance for each employee and leave type.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='leave_balances')
    year = models.IntegerField()
    
    allocated = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    used = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year', 'employee']
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} ({self.year})"
    
    def update_balance(self):
        """Update balance based on allocated and used."""
        self.balance = self.allocated - self.used
        self.save()
