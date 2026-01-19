from django.contrib import admin
from .models import Tontine, TontineMember

# Register your models here.

@admin.register(Tontine)
class TontineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'manager', 'status', 'total_pot', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'code', 'manager__username')

@admin.register(TontineMember)
class TontineMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'tontine', 'status', 'joined_date', 'total_contributed')
    list_filter = ('status',)
    search_fields = ('user__username', 'tontine__name')