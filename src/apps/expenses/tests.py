import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from apps.condo.models import Condominium, Department
from apps.expenses.models import CommonExpense, ExpenseBill
from apps.expenses.services import ExpenseCalculatorService


@pytest.mark.django_db
def test_expense_calculator_service():
    """
    Verifica que el servicio prorratee de forma exacta según el % de alícuota.
    """
    # 1. Setup
    condo = Condominium.objects.create(
        name="Condominio Test",
        rut="11.111.111-1",
        address="Calle Falsa 123"
    )
    
    # Depto con 25% de alícuota
    dept = Department.objects.create(
        condominium=condo,
        number="101",
        share_percentage=Decimal('0.250000')
    )

    # Gasto global de $100.000
    expense = CommonExpense.objects.create(
        condominium=condo,
        title="Gasto Test",
        period=timezone.now().date().replace(day=1),
        total_amount=Decimal('100000.00')
    )

    due_date = timezone.now().date() + timedelta(days=15)

    # 2. Ejecución del servicio
    count = ExpenseCalculatorService.generate_bills_for_expense(expense, due_date)

    # 3. Assertions
    bill = ExpenseBill.objects.get(department=dept, common_expense=expense)
    assert count == 1
    assert bill.calculated_amount == Decimal('25000.00')  # 25% de 100.000
    assert bill.status == ExpenseBill.Status.PENDING
    assert expense.is_closed is True