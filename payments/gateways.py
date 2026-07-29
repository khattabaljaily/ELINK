from abc import ABC, abstractmethod

import requests
from django.conf import settings

from .models import Payment


class PaymentGatewayError(Exception):
    """Raised when a gateway can't be reached, or rejects a request."""


class BasePaymentGateway(ABC):
    """Contract every payment gateway (COD, PayPal, card, ...) must implement.

    Order and cart logic only ever talk to this interface, never to a
    concrete gateway, so a real gateway can be dropped in later without
    touching the rest of the codebase.
    """

    code = None
    label = None

    # Gateways that send the customer to a hosted payment page (anything but
    # COD) set this so the checkout view redirects there instead of going
    # straight to the confirmation page.
    redirect_required = False

    @abstractmethod
    def initiate_payment(self, order) -> Payment:
        """Create (or return) the Payment record for an order.

        For redirect gateways, also sets a transient `.redirect_url`
        attribute on the returned Payment for the checkout view to send the
        customer to — it isn't a model field, so it's never persisted.
        """
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


class MyFatoorahGateway(BasePaymentGateway):
    """Hosted card checkout via MyFatoorah.

    Everything here only depends on MYFATOORAH_API_KEY / MYFATOORAH_BASE_URL
    (settings.py, sourced from secrets.json) — going live is just swapping
    those from MyFatoorah's test values to the real ones, nothing else in
    the codebase needs to change.
    """

    code = 'card'
    label = 'Card (Visa/Mastercard)'
    redirect_required = True

    def _request(self, path, payload):
        try:
            response = requests.post(
                f'{settings.MYFATOORAH_BASE_URL}{path}',
                json=payload,
                headers={
                    'Authorization': f'Bearer {settings.MYFATOORAH_API_KEY}',
                    'Content-Type': 'application/json',
                },
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise PaymentGatewayError(f'Could not reach the payment provider: {exc}') from exc

        data = response.json()
        if not data.get('IsSuccess'):
            raise PaymentGatewayError(data.get('Message') or 'The payment provider rejected the request.')
        return data['Data']

    def initiate_payment(self, order) -> Payment:
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total,
                'gateway': self.code,
                'status': Payment.Status.PENDING,
            },
        )

        # The customer lands back here whether they paid or bailed out —
        # GetPaymentStatus (in the callback view) is what tells them apart.
        callback_url = f'{settings.SITE_URL}/payments/myfatoorah/callback/'
        invoice = self._request('/v2/SendPayment', {
            'InvoiceValue': float(order.total),
            'CustomerName': order.full_name,
            'CustomerEmail': order.email,
            'CustomerMobile': order.phone,
            # Lets the callback find its way back to this order — MyFatoorah
            # echoes it back verbatim in GetPaymentStatus.
            'CustomerReference': str(order.guest_token),
            'CallBackUrl': callback_url,
            'ErrorUrl': callback_url,
            'DisplayCurrencyIso': 'QAR',
            'Language': 'en',
        })

        payment.transaction_id = str(invoice['InvoiceId'])
        payment.save(update_fields=['transaction_id', 'updated_at'])
        payment.redirect_url = invoice['InvoiceURL']
        return payment

    def get_payment_status(self, key, key_type='InvoiceId'):
        return self._request('/v2/GetPaymentStatus', {'Key': key, 'KeyType': key_type})

    def verify_payment(self, payment: Payment) -> bool:
        data = self.get_payment_status(payment.transaction_id, key_type='InvoiceId')
        is_paid = data.get('InvoiceStatus') == 'Paid'
        payment.status = Payment.Status.PAID if is_paid else Payment.Status.FAILED
        payment.save(update_fields=['status', 'updated_at'])
        return is_paid
