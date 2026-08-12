import pytest
from unittest.mock import patch
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from apps.condo.models import Condominium, Department
from apps.expenses.models import CommonExpense, ExpenseBill
from apps.payments.models import TransbankTransaction
from apps.payments.services import TransbankService


@pytest.mark.django_db
@patch('transbank.webpay.webpay_plus.transaction.Transaction.create')
def test_transbank_service_create_transaction(mock_tbk_create):
    """
    Verifica la inicialización de transacciones sanitizando parámetros para la API de Transbank.
    """
    # 1. Configuración del Mock de Transbank SDK
    mock_tbk_create.return_value = {
        'token': 'mock_tbk_token_123456789',
        'url': 'https://webpay3gint.transbank.cl/webpayserver/initTransaction'
    }

    # 2. Setup de datos
    user = User.objects.create_user(username="u1", email="u1@test.cl", password="123", role=User.Role.RESIDENTE)
    condo = Condominium.objects.create(name="Condo TBK", rut="44.444.444-4", address="Av. TBK 100")
    dept = Department.objects.create(condominium=condo, number="501", resident=user, share_percentage=Decimal('1.00'))
    
    expense = CommonExpense.objects.create(
        condominium=condo, title="Gasto TBK", period=timezone.now().date(), total_amount=Decimal('50000.00')
    )
    bill = ExpenseBill.objects.create(
        department=dept, common_expense=expense, calculated_amount=Decimal('50000.00'), due_date=timezone.now().date()
    )

    # 3. Ejecución del servicio
    tbk_service = TransbankService()
    response, buy_order, session_id = tbk_service.create_transaction(
        bill=bill, return_url="http://localhost:8000/payments/webpay-return/"
    )

    # 4. Assertions
    assert response['token'] == 'mock_tbk_token_123456789'
    assert buy_order.startswith('O')
    assert len(buy_order) <= 26  # Límite estricto del OpenAPI de Transbank
    assert buy_order.isalnum() is True  # Validación alfanumérica sin guiones


@pytest.mark.django_db
def test_transbank_transaction_model_creation():
    """
    Verifica la creación del registro inmutable de auditoría para la transacción.
    """
    user = User.objects.create_user(username="u2", email="u2@test.cl", password="123")
    condo = Condominium.objects.create(name="Condo Tx", rut="55.555.555-5", address="Av. Tx 200")
    dept = Department.objects.create(condominium=condo, number="102", resident=user, share_percentage=Decimal('1.00'))
    expense = CommonExpense.objects.create(condominium=condo, title="Gasto Tx", period=timezone.now().date(), total_amount=Decimal('10000.00'))
    bill = ExpenseBill.objects.create(department=dept, common_expense=expense, calculated_amount=Decimal('10000.00'), due_date=timezone.now().date())

    tx = TransbankTransaction.objects.create(
        bill=bill,
        buy_order="O1234567890",
        session_id="S10212345",
        tbk_token="mock_token",
        amount=Decimal('10000.00')
    )

    assert tx.status == TransbankTransaction.TransactionStatus.INITIALIZED
    assert str(tx.amount) == '10000.00'