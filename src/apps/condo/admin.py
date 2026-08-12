from django.contrib import admin
from .models import Condominium, Department


@admin.register(Condominium)
class CondominiumAdmin(admin.ModelAdmin):
    list_display = ['name', 'rut', 'address', 'created_at']
    search_fields = ['name', 'rut']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['number', 'condominium', 'resident', 'share_percentage', 'parking_number', 'storage_number', 'is_active']
    list_filter = ['condominium', 'is_active', 'floor']
    search_fields = ['number', 'resident__email', 'resident__first_name', 'resident__last_name']
    raw_id_fields = ['resident']  # Optimiza la búsqueda de residentes en condominios con miles de usuarios