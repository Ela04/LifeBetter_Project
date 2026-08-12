from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.condo.models import Condominium, Department


class CommonArea(models.Model):
    """
    Representa un área o espacio común reservable dentro de la comunidad.
    """
    condominium = models.ForeignKey(
        Condominium, 
        on_delete=models.CASCADE, 
        related_name="espacios_comunes",
        verbose_name="Condominio"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Espacio")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción / Reglamento")
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], 
        verbose_name="Aforo Máximo (Personas)"
    )
    fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Tarifa por Reserva ($)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Disponible")

    class Meta:
        verbose_name = "Espacio Común"
        verbose_name_plural = "Espacios Comunes"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.condominium.name}"


class Reservation(models.Model):
    """
    Registro de reserva de un espacio común efectuado por un departamento.
    """
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    common_area = models.ForeignKey(
        CommonArea, 
        on_delete=models.CASCADE, 
        related_name="reservations",
        verbose_name="Espacio Común"
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name="reservations",
        verbose_name="Departamento"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="reservations",
        verbose_name="Usuario Solicitante"
    )
    start_time = models.DateTimeField(verbose_name="Fecha/Hora Inicio")
    end_time = models.DateTimeField(verbose_name="Fecha/Hora Término")
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.CONFIRMED,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-start_time']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F('start_time')),
                name='reservation_end_time_after_start_time'
            )
        ]

    def clean(self):
        """
        Validación de negocio: Prevenir colisiones de reservas en el mismo horario.
        """
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("La fecha de término debe ser posterior a la fecha de inicio.")

        # Buscar traslapes: (StartA < EndB) AND (EndA > StartB)
        overlapping_query = Reservation.objects.filter(
            common_area=self.common_area,
            status=self.Status.CONFIRMED,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        
        if self.pk:
            overlapping_query = overlapping_query.exclude(pk=self.pk)

        if overlapping_query.exists():
            raise ValidationError("El espacio ya se encuentra reservado en el rango horario seleccionado.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.common_area.name} | Depto {self.department.number} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"