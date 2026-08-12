from django.db import models
from django.core.validators import MinValueValidator
from apps.condo.models import Condominium, Department


class CommonExpense(models.Model):
    """
    Representa un gasto global del condominio para un periodo determinado (ej: Mantención, Agua, Luz).
    """
    condominium = models.ForeignKey(
        Condominium, 
        on_delete=models.CASCADE, 
        related_name="common_expenses",
        verbose_name="Condominio"
    )
    title = models.CharField(max_length=200, verbose_name="Título del Gasto")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción / Detalle")
    period = models.DateField(help_text="Primer día del mes del cobro (ej: 2026-08-01)", verbose_name="Periodo")
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="Monto Total a Prorratear"
    )
    is_closed = models.BooleanField(default=False, verbose_name="¿Cerrado / Liquidado?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gasto Común Global"
        verbose_name_plural = "Gastos Comunes Globales"
        ordering = ['-period']

    def __str__(self):
        return f"{self.title} - {self.condominium.name} ({self.period.strftime('%Y-%m')})"


class ExpenseBill(models.Model):
    """
    Boleta o cobro individual emitido a un departamento específico según su alícuota.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PAID = 'PAID', 'Pagado'
        OVERDUE = 'OVERDUE', 'Moroso'

    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name="bills",
        verbose_name="Departamento"
    )
    common_expense = models.ForeignKey(
        CommonExpense, 
        on_delete=models.CASCADE, 
        related_name="bills",
        verbose_name="Gasto Común Asociado"
    )
    calculated_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Monto Calculado por Alícuota"
    )
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado de Pago"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Boleta de Gasto Común"
        verbose_name_plural = "Boletas de Gastos Comunes"
        unique_together = ('department', 'common_expense')
        ordering = ['-due_date']

    def __str__(self):
        return f"Boleta Depto {self.department.number} - ${self.calculated_amount:,} ({self.get_status_display()})"