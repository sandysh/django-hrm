from typing import Optional, Any
from datetime import date
from django.db.models import QuerySet
from reports.models import (
    TaxSlab,
    FiscalYear,
    EmployeeTax,
    FundsType,
    EmployeeFund,
    Payroll,
    Allowance,
    EmployeeAllowance,
)
from employees.models import Employee

def create_tax_slab(name: str, min_salary: float, max_salary: float, tax_rate: int, fiscal_year: FiscalYear) -> TaxSlab:
    """Create a new TaxSlab record."""
    return TaxSlab.objects.create(
        name=name, min_salary=min_salary, max_salary=max_salary, tax_rate=tax_rate, fiscal_year=fiscal_year
    )

def get_all_tax_slabs() -> QuerySet[TaxSlab]:
    """Retrieve all TaxSlab records ordered by minimum salary."""
    return TaxSlab.objects.all().order_by('min_salary')

def get_tax_slab_by_id(slab_id: int) -> Optional[TaxSlab]:
    """Retrieve a specific TaxSlab by its ID."""
    return TaxSlab.objects.filter(id=slab_id).first()

def get_applicable_tax_slab(salary: float) -> Optional[TaxSlab]:
    """Retrieve the matching tax slab for a given salary amount."""
    return TaxSlab.objects.filter(min_salary__lte=salary, max_salary__gte=salary).first()

def update_tax_slab(slab_id: int, **kwargs: Any) -> Optional[TaxSlab]:
    """Update specific fields of a TaxSlab by ID."""
    slab = get_tax_slab_by_id(slab_id)
    if slab:
        for key, value in kwargs.items():
            setattr(slab, key, value)
        slab.save()
    return slab

def delete_tax_slab(slab_id: int) -> bool:
    """Delete a TaxSlab by its ID. Returns True if deleted, False otherwise."""
    slab = get_tax_slab_by_id(slab_id)
    if slab:
        slab.delete()
        return True
    return False

def create_fiscal_year(start_date: date, end_date: date, is_active: bool, name: str = "") -> FiscalYear:
    """Create a new FiscalYear record."""
    return FiscalYear.objects.create(
        name=name, start_date=start_date, end_date=end_date, is_active=is_active
    )

def get_active_fiscal_year() -> Optional[FiscalYear]:
    """Retrieve the currently active FiscalYear."""
    return FiscalYear.objects.filter(is_active=True).first()

def get_all_fiscal_years() -> QuerySet[FiscalYear]:
    """Retrieve all FiscalYear records ordered by descending start date."""
    return FiscalYear.objects.all().order_by('-start_date')

def get_fiscal_year_by_id(fy_id: int) -> Optional[FiscalYear]:
    """Retrieve a specific FiscalYear by its ID."""
    return FiscalYear.objects.filter(id=fy_id).first()

def update_fiscal_year(fy_id: int, **kwargs: Any) -> Optional[FiscalYear]:
    """Update specific fields of a FiscalYear by ID."""
    fy = get_fiscal_year_by_id(fy_id)
    if fy:
        for key, value in kwargs.items():
            setattr(fy, key, value)
        fy.save()
    return fy

def delete_fiscal_year(fy_id: int) -> bool:
    """Delete a FiscalYear by its ID. Returns True if deleted, False otherwise."""
    fy = get_fiscal_year_by_id(fy_id)
    if fy:
        fy.delete()
        return True
    return False

def create_employee_tax(employee: Employee, taxslab: TaxSlab, taxable_amount: float) -> EmployeeTax:
    """Create a new EmployeeTax record linking an employee to a tax slab."""
    return EmployeeTax.objects.create(
        employee=employee, taxslab=taxslab, taxable_amount=taxable_amount
    )

def get_employee_taxes(employee: Employee) -> QuerySet[EmployeeTax]:
    """Retrieve all EmployeeTax records for a specific employee."""
    return EmployeeTax.objects.filter(employee=employee).select_related('taxslab')

def get_employee_tax_by_id(tax_id: int) -> Optional[EmployeeTax]:
    """Retrieve a specific EmployeeTax record by its ID."""
    return EmployeeTax.objects.filter(id=tax_id).first()

def update_employee_tax(tax_id: int, **kwargs: Any) -> Optional[EmployeeTax]:
    """Update specific fields of an EmployeeTax record by ID."""
    emp_tax = get_employee_tax_by_id(tax_id)
    if emp_tax:
        for key, value in kwargs.items():
            setattr(emp_tax, key, value)
        emp_tax.save()
    return emp_tax

def delete_employee_tax(tax_id: int) -> bool:
    """Delete an EmployeeTax record by its ID. Returns True if deleted, False otherwise."""
    emp_tax = get_employee_tax_by_id(tax_id)
    if emp_tax:
        emp_tax.delete()
        return True
    return False

def create_fund_type(name: str, emp_contribution: int, org_contribution: int) -> FundsType:
    """Create a new FundsType record."""
    return FundsType.objects.create(
        name=name, emp_contribution=emp_contribution, org_contribution=org_contribution
    )

def get_all_fund_types() -> QuerySet[FundsType]:
    """Retrieve all FundsType records."""
    return FundsType.objects.all()

def get_fund_type_by_id(fund_id: int) -> Optional[FundsType]:
    """Retrieve a specific FundsType record by its ID."""
    return FundsType.objects.filter(id=fund_id).first()

def update_fund_type(fund_id: int, **kwargs: Any) -> Optional[FundsType]:
    """Update specific fields of a FundsType record by ID."""
    fund = get_fund_type_by_id(fund_id)
    if fund:
        for key, value in kwargs.items():
            setattr(fund, key, value)
        fund.save()
    return fund

def delete_fund_type(fund_id: int) -> bool:
    """Delete a FundsType record by its ID. Returns True if deleted, False otherwise."""
    fund = get_fund_type_by_id(fund_id)
    if fund:
        fund.delete()
        return True
    return False

def create_employee_fund(employee: Employee, funds: FundsType) -> EmployeeFund:
    """Create a new EmployeeFund record linking an employee to a fund type."""
    return EmployeeFund.objects.create(employee=employee, funds=funds)

def get_employee_funds(employee: Employee) -> QuerySet[EmployeeFund]:
    """Retrieve all EmployeeFund records for a specific employee."""
    return EmployeeFund.objects.filter(employee=employee).select_related('funds')

def get_employee_fund_by_id(emp_fund_id: int) -> Optional[EmployeeFund]:
    """Retrieve a specific EmployeeFund record by its ID."""
    return EmployeeFund.objects.filter(id=emp_fund_id).first()

def update_employee_fund(emp_fund_id: int, **kwargs: Any) -> Optional[EmployeeFund]:
    """Update specific fields of an EmployeeFund record by ID."""
    emp_fund = get_employee_fund_by_id(emp_fund_id)
    if emp_fund:
        for key, value in kwargs.items():
            setattr(emp_fund, key, value)
        emp_fund.save()
    return emp_fund

def delete_employee_fund(emp_fund_id: int) -> bool:
    """Delete an EmployeeFund record by its ID. Returns True if deleted, False otherwise."""
    emp_fund = get_employee_fund_by_id(emp_fund_id)
    if emp_fund:
        emp_fund.delete()
        return True
    return False

def create_payroll(employee: Employee, total_payable: float, fine_deduction: int) -> Payroll:
    """Create a new Payroll record for an employee."""
    return Payroll.objects.create(
        employee=employee, total_payable=total_payable, fine_deduction=fine_deduction
    )

def get_all_payrolls() -> QuerySet[Payroll]:
    """Retrieve all Payroll records with pre-fetched employee data."""
    return Payroll.objects.all().select_related('employee')

def get_employee_payrolls(employee: Employee) -> QuerySet[Payroll]:
    """Retrieve all Payroll records for a specific employee."""
    return Payroll.objects.filter(employee=employee)

def get_payroll_by_id(payroll_id: int) -> Optional[Payroll]:
    """Retrieve a specific Payroll record by its ID."""
    return Payroll.objects.filter(id=payroll_id).first()

def update_payroll(payroll_id: int, **kwargs: Any) -> Optional[Payroll]:
    """Update specific fields of a Payroll record by ID."""
    payroll = get_payroll_by_id(payroll_id)
    if payroll:
        for key, value in kwargs.items():
            setattr(payroll, key, value)
        payroll.save()
    return payroll

def delete_payroll(payroll_id: int) -> bool:
    """Delete a Payroll record by its ID. Returns True if deleted, False otherwise."""
    payroll = get_payroll_by_id(payroll_id)
    if payroll:
        payroll.delete()
        return True
    return False

def create_allowance(name: str, amount: int) -> Allowance:
    """Create a new Allowance record."""
    return Allowance.objects.create(name=name, amount=amount)

def get_all_allowances() -> QuerySet[Allowance]:
    """Retrieve all Allowance records."""
    return Allowance.objects.all()

def get_allowance_by_id(allowance_id: int) -> Optional[Allowance]:
    """Retrieve a specific Allowance record by its ID."""
    return Allowance.objects.filter(id=allowance_id).first()

def update_allowance(allowance_id: int, **kwargs: Any) -> Optional[Allowance]:
    """Update specific fields of an Allowance record by ID."""
    allowance = get_allowance_by_id(allowance_id)
    if allowance:
        for key, value in kwargs.items():
            setattr(allowance, key, value)
        allowance.save()
    return allowance

def delete_allowance(allowance_id: int) -> bool:
    """Delete an Allowance record by its ID. Returns True if deleted, False otherwise."""
    allowance = get_allowance_by_id(allowance_id)
    if allowance:
        allowance.delete()
        return True
    return False

def create_employee_allowance(emp: Employee, allowance: Allowance) -> EmployeeAllowance:
    """Create a new EmployeeAllowance record linking an employee to an allowance."""
    return EmployeeAllowance.objects.create(emp=emp, allowance=allowance)

def get_employee_allowances(employee: Employee) -> QuerySet[EmployeeAllowance]:
    """Retrieve all EmployeeAllowance records for a specific employee."""
    return EmployeeAllowance.objects.filter(emp=employee).select_related('allowance')

def get_employee_allowance_by_id(emp_allowance_id: int) -> Optional[EmployeeAllowance]:
    """Retrieve a specific EmployeeAllowance record by its ID."""
    return EmployeeAllowance.objects.filter(id=emp_allowance_id).first()

def update_employee_allowance(emp_allowance_id: int, **kwargs: Any) -> Optional[EmployeeAllowance]:
    """Update specific fields of an EmployeeAllowance record by ID."""
    emp_allowance = get_employee_allowance_by_id(emp_allowance_id)
    if emp_allowance:
        for key, value in kwargs.items():
            setattr(emp_allowance, key, value)
        emp_allowance.save()
    return emp_allowance

def delete_employee_allowance(emp_allowance_id: int) -> bool:
    """Delete an EmployeeAllowance record by its ID. Returns True if deleted, False otherwise."""
    emp_allowance = get_employee_allowance_by_id(emp_allowance_id)
    if emp_allowance:
        emp_allowance.delete()
        return True
    return False
