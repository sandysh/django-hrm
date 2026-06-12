from django.db import models
from core.models import BaseModel
from decimal import ROUND_HALF_UP, Decimal

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

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

class TaxSlab(BaseModel):
    name = models.CharField(max_length=50)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.IntegerField()
    
class FiscalYear(BaseModel):
    name=models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active=models.BooleanField()
    
    def save(self, *args , **kwargs):
        self.name=f'FY {self.start_date.year}-{self.end_date.year}'
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
    org_comntribution=models.IntegerField()
    
    
class EmployeeFund(BaseModel):
    employee=models.ForeignKey("employees.Employee", on_delete=models.CASCADE)
    funds=models.ForeignKey(FundsType , on_delete=models.CASCADE)
      
      
class Payroll(models.Model):
    employee=models.ForeignKey("employees.Employee" , on_delete=models.CASCADE)
    total_payable=models.DecimalField(decimal_places=2 , max_digits=2)
    fine_deduction=models.IntegerField()
    
    
class Allowance(BaseModel):
    name=models.CharField(max_length=70)
    amount=models.IntegerField()
    
class EmployeeAllowance(BaseModel):
    emp=models.ForeignKey("employees.Employee" , on_delete=models.CASCADE)
    allowance=models.ForeignKey("Allowance", on_delete=models.CASCADE)
