from django.contrib import admin, messages
from django.utils import timezone
from datetime import timedelta
from .models import CommonExpense, ExpenseBill
from .services import ExpenseCalculatorService


@admin.action(description="Generar boletas prorrateadas para este Gasto Común")
def calculate_bills_action(modeladmin, request, queryset):
    for expense in queryset:
        if expense.is_closed:
            modeladmin.message_user(
                request, 
                f"El gasto {expense.title} ya fue cerrado previamente.", 
                level=messages.WARNING
            )
            continue

        # Vencimiento por defecto: 15 días tras la creación
        due_date = timezone.now().date() + timedelta(days=15)
        count = ExpenseCalculatorService.generate_bills_for_expense(expense, due_date)
        modeladmin.message_user(
            request, 
            f"Se generaron exitosamente {count} boletas para {expense.title}.", 
            level=messages.SUCCESS
        )


@admin.register(CommonExpense)
class CommonExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'condominium', 'period', 'total_amount', 'is_closed', 'created_at']
    list_filter = ['condominium', 'is_closed', 'period']
    search_fields = ['title']
    actions = [calculate_bills_action]


@admin.register(ExpenseBill)
class ExpenseBillAdmin(admin.ModelAdmin):
    list_display = ['department', 'common_expense', 'calculated_amount', 'due_date', 'status']
    list_filter = ['status', 'due_date', 'department__condominium']
    search_fields = ['department__number', 'department__resident__email']
    raw_id_fields = ['department', 'common_expense']