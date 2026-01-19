from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'user_type', 'is_staff', 'is_verified')
    list_filter = ('user_type', 'is_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('phone_number', 'user_type', 'profile_picture', 'is_verified'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

