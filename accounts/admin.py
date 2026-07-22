from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class ELinkUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Contact info', {'fields': ('phone', 'address', 'city')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
