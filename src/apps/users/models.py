# src/apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema LifeBetter.
    Soporta Roles (RBAC) y extiende los campos estándar de Django.
    """
    @property
    def is_admin_or_staff(self):
        """Devuelve True si el usuario tiene rol ADMIN o permisos de staff en Django."""
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CONSERJE = 'CONSERJE', 'Conserje'
        RESIDENTE = 'RESIDENTE', 'Residente'

    email = models.EmailField(
        unique=True, 
        verbose_name="Correo Electrónico",
        error_messages={'unique': 'Ya existe un usuario registrado con este correo.'}
    )
    role = models.CharField(
        max_length=15, 
        choices=Role.choices, 
        default=Role.RESIDENTE,
        verbose_name="Rol de Usuario"
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Teléfono de Contacto"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"