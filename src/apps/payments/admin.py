from django.contrib import admin
from .models import TransbankTransaction


@admin.register(TransbankTransaction)
class TransbankTransactionAdmin(admin.ModelAdmin):
    list_display = ['buy_order', 'bill', 'amount', 'status', 'authorization_code', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buy_order', 'authorization_code', 'bill__department__number']
    readonly_fields = ['id', 'buy_order', 'session_id', 'tbk_token', 'amount', 'authorization_code', 'response_code', 'created_at', 'updated_at']