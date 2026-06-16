from django.db import models
from core.models import BaseModel
from decimal import ROUND_HALF_UP, Decimal
from django.contrib.contenttypes.models import ContentType


class logType(models.TextChoices):
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'
    CREATE = 'CREATE', 'Create'
    UPDATE = 'UPDATE', 'Update'
    DELETE = 'DELETE', 'Delete'
    EMAIL_SENT = 'EMAIL_SENT', 'Email Sent'
    REPORT_GENERATED = 'REPORT_GENERATED', 'Report Generated'
    
# Create your models here.
class AuditLog(models.Model):
    user= models.ForeignKey("employees.Employee", on_delete=models.CASCADE , null=True, blank=True)
    action = models.CharField(max_length=50, choices=logType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=64, null=True, blank=True)
    module_name=models.CharField(max_length=50, null=True, blank=True)
    json_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

class TaxSlab(BaseModel):
    name = models.CharField(max_length=50)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.IntegerField()
    fiscal_year=models.ForeignKey("reports.FiscalYear", on_delete=models.CASCADE, null=True, blank=True)
    
class FiscalYear(BaseModel):
    name=models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active=models.BooleanField()
    
    def save(self, *args , **kwargs):
        from django.utils.dateparse import parse_date
        
        start = self.start_date
        end = self.end_date
        
        if isinstance(start, str):
            start = parse_date(start)
        if isinstance(end, str):
            end = parse_date(end)
            
        if start and end:
            self.name=f'FY {start.year}-{end.year}'
        else:
            self.name='FY Unknown'
            
        return super().save(*args,**kwargs)
    
class EmployeeTax(BaseModel):
    employee=models.ForeignKey("employees.Employee", on_delete=models.CASCADE)
    taxslab=models.ForeignKey(TaxSlab, on_delete=models.CASCADE)
    taxable_amount=models.DecimalField(max_digits=12, decimal_places=2)
    
    @property
    def calculated_tax(self):
        return (
            (self.taxslab.tax_rate / Decimal("100"))
            * self.employee.basic_salary
        ) 
                        
class FundsType(BaseModel):
    name=models.CharField(max_length=50)
    emp_contribution=models.IntegerField()
    org_contribution=models.IntegerField()
    
    @property
    def employee_count(self):
        return self.employeefund_set.count() if hasattr(self, 'employeefund_set') else 0
     
class EmployeeFund(BaseModel): # M:M table for employee and fund since  employee can have multiple funds
    employee=models.ForeignKey("employees.Employee", on_delete=models.CASCADE)
    funds=models.ForeignKey(FundsType , on_delete=models.CASCADE)
        
class Payroll(models.Model):
    employee=models.ForeignKey("employees.Employee" , on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True) # To specify which month it is

    # Profile & Shift
    effective_working_days = models.IntegerField(default=0)

    # Attendance Summary
    days_present = models.IntegerField(default=0)
    total_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    leave_days_taken = models.IntegerField(default=0)
    unpaid_absent_days = models.IntegerField(default=0)

    # Violations Summary
    late_arrivals = models.IntegerField(default=0)
    early_departures = models.IntegerField(default=0)
    missing_checkouts = models.IntegerField(default=0)
    three_late_arrivals = models.IntegerField(default=0)

    # Calculated Salary (Earnings)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    earned_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Calculated Salary (Deductions)
    late_penalty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    three_late_penalty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Final
    total_payable=models.DecimalField(decimal_places=2 , max_digits=12, default=0)
    fine_deduction=models.DecimalField(decimal_places=2, max_digits=12, default=0)
    
class Allowance(BaseModel):
    name=models.CharField(max_length=70)
    amount=models.IntegerField()
    
class EmployeeAllowance(BaseModel): # M:M table for employee and allowance since  employee can have multiple allowance
    emp=models.ForeignKey("employees.Employee" , on_delete=models.CASCADE)
    allowance=models.ForeignKey("Allowance", on_delete=models.CASCADE)
