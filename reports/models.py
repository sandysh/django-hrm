from django.db import models
from employees.models import Employee

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
    user= models.ForeignKey(Employee, on_delete=models.CASCADE , null=True, blank=True)

    action = models.CharField(max_length=50, choices=logType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
    
class payroll(models.Model):
    employee=models.ForeignKey(Employee , on_delete=models.CASCADE)
    total_payable=models.DecimalField(decimal_places=2 , max_digits=2)
    fine_deduction=models.IntegerField()
    