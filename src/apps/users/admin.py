from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del panel de administración para CustomUser.
    Permite visualizar, filtrar y editar los campos del modelo RBAC (Role, Teléfono).
    """
    model = User
    list_display = ['email', 'username', 'role', 'phone_number', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']

    # Campos al editar un usuario existente
    fieldsets = UserAdmin.fieldsets + (
        ('Atributos de Dominio (LifeBetter RBAC)', {'fields': ('role', 'phone_number')}),
    )

    # Campos al crear un usuario nuevo desde el Admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Atributos de Dominio (LifeBetter RBAC)', {'fields': ('email', 'role', 'phone_number')}),
    )