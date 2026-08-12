from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Condominium(models.Model):
    """
    Representa una comunidad, edificio o condominio.
    """
    name = models.CharField(max_length=150, verbose_name="Nombre del Condominio")
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT de la Comunidad")
    address = models.CharField(max_length=255, verbose_name="Dirección")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Condominio"
        verbose_name_plural = "Condominios"

    def __str__(self):
        return f"{self.name} ({self.rut})"


class Department(models.Model):
    """
    Unidad habitable o departamento dentro del condominio.
    Contiene el porcentaje de alícuota para el cálculo exacto de gastos comunes.
    """
    condominium = models.ForeignKey(
        Condominium, 
        on_delete=models.CASCADE, 
        related_name="departments",
        verbose_name="Condominio"
    )
    number = models.CharField(max_length=10, verbose_name="Número de Depto")
    floor = models.IntegerField(default=1, verbose_name="Piso")
    parking_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Estacionamiento")
    storage_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Bodega")
    
    # Usuario residente asignado (Soporta CustomUser de apps.users)
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments",
        verbose_name="Residente Asignado"
    )

    # Alícuota / Porcentaje de participación (Ej: 0.025000 = 2.5%)
    share_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=6,
        validators=[
            MinValueValidator(0.000001),
            MaxValueValidator(1.000000)
        ],
        verbose_name="Alícuota / Porcentaje de Participación",
        help_text="Expresado en decimales. Ej: 0.025000 representa un 2.5% del total del edificio."
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        unique_together = ('condominium', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Depto {self.number} - {self.condominium.name}"