from django.contrib import admin
from reports.models import TaxSlab, FiscalYear, EmployeeTax, FundsType, EmployeeFund, Payroll, Allowance , AuditLog

# Register your models here.
admin.site.register(AuditLog)
admin.site.register(TaxSlab)
admin.site.register(FiscalYear)
admin.site.register(EmployeeTax)
admin.site.register(FundsType)
admin.site.register(EmployeeFund)
admin.site.register(Allowance)
admin.site.register(Payroll)