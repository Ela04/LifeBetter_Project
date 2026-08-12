import uuid
from django.db import models
from apps.expenses.models import ExpenseBill


class TransbankTransaction(models.Model):
    """
    Registro inmutable de auditoría para cada intento de pago realizado mediante Webpay Plus.
    """
    class TransactionStatus(models.TextChoices):
        INITIALIZED = 'INITIALIZED', 'Inicializada'
        AUTHORIZED = 'AUTHORIZED', 'Autorizada'
        FAILED = 'FAILED', 'Fallida / Rechazada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill = models.ForeignKey(
        ExpenseBill, 
        on_delete=models.CASCADE, 
        related_name="transactions",
        verbose_name="Boleta Asociada"
    )
    buy_order = models.CharField(max_length=26, unique=True, verbose_name="Orden de Compra")
    session_id = models.CharField(max_length=61, verbose_name="ID de Sesión")
    tbk_token = models.CharField(max_length=255, blank=True, null=True, db_index=True, verbose_name="Token Webpay")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Transaccionado")
    status = models.CharField(
        max_length=15, 
        choices=TransactionStatus.choices, 
        default=TransactionStatus.INITIALIZED,
        db_index=True,
        verbose_name="Estado de Transacción"
    )
    authorization_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código Autorización")
    response_code = models.IntegerField(blank=True, null=True, verbose_name="Código Respuesta Banco")
    payment_type_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Tipo de Pago")
    shares_number = models.IntegerField(default=0, verbose_name="Número de Cuotas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transacción Webpay"
        verbose_name_plural = "Transacciones Webpay"
        ordering = ['-created_at']

    def __str__(self):
        return f"Orden {self.buy_order} - Depto {self.bill.department.number} - [{self.get_status_display()}]"