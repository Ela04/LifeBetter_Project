# src/apps/expenses/services.py
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from .models import CommonExpense, ExpenseBill


class ExpenseCalculatorService:
    @staticmethod
    @transaction.atomic
    def generate_bills_for_expense(common_expense: CommonExpense, due_date) -> int:
        """
        Calcula y genera automáticamente las boletas individuales para cada departamento 
        basado en el porcentaje de alícuota asignado.
        """
        # Optimización ORM: traemos solo departamentos activos del condominio
        departments = common_expense.condominium.departments.filter(is_active=True)
        
        bills_to_create = []

        for dept in departments:
            # Cálculo exacto con redondeo financiero estándar (2 decimales)
            amount = (common_expense.total_amount * dept.share_percentage).quantize(
                Decimal('0.01'), 
                rounding=ROUND_HALF_UP
            )

            bills_to_create.append(
                ExpenseBill(
                    department=dept,
                    common_expense=common_expense,
                    calculated_amount=amount,
                    due_date=due_date,
                    status=ExpenseBill.Status.PENDING
                )
            )

        # Inserción masiva en base de datos para prevenir N+1 queries
        created_bills = ExpenseBill.objects.bulk_create(
            bills_to_create, 
            ignore_conflicts=True
        )

        # Marcar el gasto común como cerrado
        common_expense.is_closed = True
        common_expense.save()

        return len(created_bills)