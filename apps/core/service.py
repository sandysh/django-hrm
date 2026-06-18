from typing import Any, Optional
from django.db.models import QuerySet
from core.query import (
    create_tax_slab,
    get_all_tax_slabs,
    get_tax_slab_by_id,
    update_tax_slab,
    delete_tax_slab,
    create_fiscal_year,
    get_all_fiscal_years,
    get_active_fiscal_year,
)
from reports.models import TaxSlab, FiscalYear

class TaxSlabService:
    """Service layer for TaxSlab business logic."""

    @staticmethod
    def create_slab(name: str, min_salary: float, max_salary: float, tax_rate: int, fiscal_year: FiscalYear) -> TaxSlab:
        """Create a new tax slab."""
        # Add business validation here if necessary
        return create_tax_slab(name, min_salary, max_salary, tax_rate, fiscal_year)

    @staticmethod
    def get_all_slabs() -> QuerySet[TaxSlab]:
        """Get all tax slabs."""
        return get_all_tax_slabs()

    @staticmethod
    def get_slab(slab_id: int) -> Optional[TaxSlab]:
        """Get tax slab by ID."""
        return get_tax_slab_by_id(slab_id)

    @staticmethod
    def update_slab(slab_id: int, **kwargs: Any) -> Optional[TaxSlab]:
        """Update an existing tax slab."""
        return update_tax_slab(slab_id, **kwargs)

    @staticmethod
    def delete_slab(slab_id: int) -> bool:
        """Delete a tax slab by ID."""
        return delete_tax_slab(slab_id)

class FiscalYearService:
    """Service layer for FiscalYear business logic."""

    @staticmethod
    def create_fy(start_date, end_date, is_active=False) -> FiscalYear:
        """Create a new fiscal year."""
        return create_fiscal_year(start_date, end_date, is_active)

    @staticmethod
    def get_all_fys() -> QuerySet[FiscalYear]:
        """Get all fiscal years."""
        return get_all_fiscal_years()

    @staticmethod
    def get_active_fy() -> Optional[FiscalYear]:
        """Get the active fiscal year."""
        return get_active_fiscal_year()

from core.query import (
    create_allowance,
    get_all_allowances,
    get_allowance_by_id,
    update_allowance,
    delete_allowance,
)
from reports.models import Allowance

class AllowanceService:
    """Service layer for Allowance business logic."""

    @staticmethod
    def create_allow(name: str, amount: int) -> Allowance:
        """Create a new allowance."""
        return create_allowance(name, amount)

    @staticmethod
    def get_all_allows() -> QuerySet[Allowance]:
        """Get all allowances."""
        return get_all_allowances()

    @staticmethod
    def get_allow(allow_id: int) -> Optional[Allowance]:
        """Get allowance by ID."""
        return get_allowance_by_id(allow_id)

    @staticmethod
    def update_allow(allow_id: int, **kwargs: Any) -> Optional[Allowance]:
        """Update an existing allowance."""
        return update_allowance(allow_id, **kwargs)

    @staticmethod
    def delete_allow(allow_id: int) -> bool:
        """Delete an allowance by ID."""
        return delete_allowance(allow_id)

from core.query import (
    create_fund_type,
    get_all_fund_types,
    get_fund_type_by_id,
    update_fund_type,
    delete_fund_type,
)
from reports.models import FundsType

class FundService:
    """Service layer for Fund business logic."""

    @staticmethod
    def create_fund(name: str, emp_contribution: int, org_contribution: int) -> FundsType:
        """Create a new fund type."""
        return create_fund_type(name, emp_contribution, org_contribution)

    @staticmethod
    def get_all_funds() -> QuerySet[FundsType]:
        """Get all fund types."""
        return get_all_fund_types()

    @staticmethod
    def get_fund(fund_id: int) -> Optional[FundsType]:
        """Get fund type by ID."""
        return get_fund_type_by_id(fund_id)

    @staticmethod
    def update_fund(fund_id: int, **kwargs: Any) -> Optional[FundsType]:
        """Update an existing fund type."""
        return update_fund_type(fund_id, **kwargs)

    @staticmethod
    def delete_fund(fund_id: int) -> bool:
        """Delete a fund type by ID."""
        return delete_fund_type(fund_id)
