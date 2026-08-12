from django.contrib import admin
from .models import CommonArea, Reservation


@admin.register(CommonArea)
class CommonAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'condominium', 'capacity', 'fee', 'is_active']
    list_filter = ['condominium', 'is_active']
    search_fields = ['name']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['common_area', 'department', 'user', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'common_area__condominium', 'start_time']
    search_fields = ['department__number', 'user__email', 'common_area__name']
    raw_id_fields = ['department', 'user']