from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'gateway', 'status', 'created_at')
    list_filter = ('gateway', 'status')
