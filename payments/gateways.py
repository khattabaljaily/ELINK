from abc import ABC, abstractmethod

from .models import Payment


class BasePaymentGateway(ABC):
    """Contract every payment gateway (COD, PayPal, card, ...) must implement.

    Order and cart logic only ever talk to this interface, never to a
    concrete gateway, so a real gateway can be dropped in later without
    touching the rest of the codebase.
    """

    code = None
    label = None

    @abstractmethod
    def initiate_payment(self, order) -> Payment:
        """Create (or return) the Payment record for an order."""
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, payment: Payment) -> bool:
        """Confirm whether a payment has actually gone through."""
        raise NotImplementedError


class CashOnDeliveryGateway(BasePaymentGateway):
    """The only gateway wired up today: pay in cash when the order arrives."""

    code = 'cod'
    label = 'Cash on Delivery'

    def initiate_payment(self, order) -> Payment:
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total,
                'gateway': self.code,
                'status': Payment.Status.PENDING,
            },
        )
        return payment

    def verify_payment(self, payment: Payment) -> bool:
        if payment.status == Payment.Status.PAID:
            return True
        payment.status = Payment.Status.PAID
        payment.save(update_fields=['status', 'updated_at'])
        return True
