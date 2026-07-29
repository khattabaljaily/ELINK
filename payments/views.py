from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from orders.emails import send_new_order_admin_alert, send_order_confirmation
from orders.models import Order

from .registry import get_gateway


def myfatoorah_callback(request):
    """Where MyFatoorah sends the customer back after a payment attempt.

    MyFatoorah only gives us its own `paymentId` here, so we look the
    payment status up first and use the CustomerReference we set at
    checkout (the order's guest_token) to find our own order.
    """
    payment_id = request.GET.get('paymentId')
    gateway = get_gateway('card')

    if not payment_id:
        messages.error(request, 'Payment reference missing. Please try checking out again.')
        return redirect('cart:detail')

    data = gateway.get_payment_status(payment_id, key_type='PaymentId')
    order = get_object_or_404(Order, guest_token=data.get('CustomerReference'))
    payment = order.payment

    is_paid = data.get('InvoiceStatus') == 'Paid'
    payment.status = payment.Status.PAID if is_paid else payment.Status.FAILED
    payment.transaction_id = str(payment_id)
    payment.save(update_fields=['status', 'transaction_id', 'updated_at'])

    if is_paid:
        send_order_confirmation(request, order)
        send_new_order_admin_alert(request, order)
        return redirect('orders:confirmation', token=order.guest_token)

    messages.error(request, 'Payment wasn\'t completed. You can try again or contact us for help.')
    return redirect('orders:detail', token=order.guest_token)
