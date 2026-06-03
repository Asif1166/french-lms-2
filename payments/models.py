from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from courses.models import Course


class PaymentTransaction(models.Model):
    """
    Payment transactions for course enrollments
    """
    GATEWAY_CHOICES = [
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
        ('SSLCOMMERZ', 'SSLCommerz'),
        ('RAZORPAY', 'Razorpay'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    level = models.ForeignKey('courses.Level', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    transaction_id = models.CharField(max_length=200, unique=True, help_text="Gateway transaction ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    gateway_response = models.JSONField(null=True, blank=True, help_text="Full response from payment gateway")
    failure_reason = models.TextField(blank=True, help_text="Reason for failure if status is FAILED")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
    
    def __str__(self):
        item_name = self.course.name if self.course else (self.level.title if self.level else "Unknown")
        return f"{self.user.email} - {item_name} - {self.status} - {self.transaction_id}"


class PaymentWebhook(models.Model):
    """
    Store webhook events from payment gateways for audit
    """
    gateway = models.CharField(max_length=20)
    event_type = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=200, db_index=True)
    payload = models.JSONField()
    signature = models.TextField(blank=True, help_text="Webhook signature for verification")
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_webhooks'
        ordering = ['-created_at']
        verbose_name = 'Payment Webhook'
        verbose_name_plural = 'Payment Webhooks'
    
    def __str__(self):
        return f"{self.gateway} - {self.event_type} - {self.transaction_id}"
