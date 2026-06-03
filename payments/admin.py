from django.contrib import admin
from .models import PaymentTransaction, PaymentWebhook


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'level', 'gateway', 'amount', 'currency', 'status', 'transaction_id', 'created_at']
    list_filter = ['gateway', 'status', 'currency', 'created_at']
    search_fields = ['user__email', 'course__name', 'level__title', 'transaction_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'course', 'level', 'gateway', 'transaction_id', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'failure_reason')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ['gateway', 'event_type', 'transaction_id', 'is_processed', 'created_at']
    list_filter = ['gateway', 'event_type', 'is_processed', 'created_at']
    search_fields = ['transaction_id', 'event_type']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
