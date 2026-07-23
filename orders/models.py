from django.conf import settings
from django.db import models

from products.models import Variant


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='orders', null=True, blank=True,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    address = models.TextField()
    city = models.CharField(max_length=100)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk}'

    def recalculate_total(self):
        self.total = sum((item.subtotal for item in self.items.all()), start=0)
        self.save(update_fields=['total'])

    @property
    def is_cancellable(self):
        return self.status not in (self.Status.DELIVERED, self.Status.CANCELLED)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT, related_name='order_items')
    product_name = models.CharField(max_length=200)
    variant_label = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class ReturnRequest(models.Model):
    class Reason(models.TextChoices):
        CHANGED_MIND = 'changed_mind', 'Changed my mind'
        WRONG_ITEM = 'wrong_item', 'Wrong item received'
        NO_LONGER_NEEDED = 'no_longer_needed', 'No longer needed'
        DAMAGED = 'damaged', 'Item arrived damaged'
        DEFECTIVE = 'defective', 'Item is defective'
        OTHER = 'other', 'Other'

    class Resolution(models.TextChoices):
        REFUND = 'refund', 'Refund'
        EXCHANGE = 'exchange', 'Exchange'
        REPLACEMENT = 'replacement', 'Replacement'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    reason = models.CharField(max_length=20, choices=Reason.choices)
    resolution_requested = models.CharField(max_length=20, choices=Resolution.choices)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    staff_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Return request #{self.pk} for order #{self.order_id}'

    @property
    def is_damage_claim(self):
        return self.reason in (self.Reason.DAMAGED, self.Reason.DEFECTIVE)
