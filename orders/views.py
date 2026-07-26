from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.utils import get_cart
from coupons.services import CouponError, calculate_discount, get_valid_coupon_for_cart, redeem_coupon_for_order
from payments.registry import get_gateway
from products.models import Variant

from .emails import send_order_confirmation, send_order_status_update, send_return_request_received
from .forms import READY_PAYMENT_METHODS, CheckoutForm, ReturnRequestForm
from .models import Order, OrderItem


class InsufficientStockError(Exception):
    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(product_name)


def checkout(request):
    cart = get_cart(request)

    if not cart.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart:detail')

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': request.user.phone,
            'address': request.user.address,
            'city': request.user.city,
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.save()

                    for item in cart.items.select_related('variant__product'):
                        variant = Variant.objects.select_related('product').select_for_update().get(
                            pk=item.variant_id,
                        )
                        if variant.stock < item.quantity:
                            raise InsufficientStockError(variant.product.name)

                        OrderItem.objects.create(
                            order=order,
                            variant=variant,
                            product_name=variant.product.name,
                            variant_label=' / '.join(p for p in (variant.size, variant.color) if p),
                            unit_price=variant.price,
                            quantity=item.quantity,
                        )
                        variant.stock -= item.quantity
                        variant.save(update_fields=['stock'])

                    order.recalculate_total()

                    if cart.coupon_code:
                        redeem_coupon_for_order(order, cart.coupon_code)
                        order.save(update_fields=['coupon_code', 'discount_total'])
                        order.recalculate_total()

                    gateway = get_gateway(form.cleaned_data['payment_method'])
                    gateway.initiate_payment(order)

                    cart.items.all().delete()
                    if cart.coupon_code:
                        cart.coupon_code = ''
                        cart.save(update_fields=['coupon_code'])
            except InsufficientStockError as exc:
                messages.error(
                    request,
                    f'Sorry, "{exc.product_name}" no longer has enough stock. Please update your cart.',
                )
                return redirect('cart:detail')
            except CouponError as exc:
                messages.error(request, exc.message)
                return redirect('cart:detail')

            send_order_confirmation(request, order)
            return redirect('orders:confirmation', token=order.guest_token)
    else:
        form = CheckoutForm(initial=initial)

    coupon = get_valid_coupon_for_cart(cart)
    discount = calculate_discount(cart)
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart,
        'ready_payment_methods': READY_PAYMENT_METHODS,
        'coupon': coupon,
        'discount_amount': discount,
        'total_after_discount': cart.total_price - discount,
    })


def confirmation(request, token):
    order = get_object_or_404(Order, guest_token=token)
    return render(request, 'orders/confirmation.html', {'order': order})


def order_detail(request, token):
    order = get_object_or_404(
        Order.objects.prefetch_related('return_requests'), guest_token=token,
    )
    open_return_request = next(
        (r for r in order.return_requests.all() if r.status in ('pending', 'approved')), None,
    )
    return render(request, 'orders/detail.html', {
        'order': order,
        'open_return_request': open_return_request,
    })


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if request.method == 'POST':
        if not order.is_cancellable:
            messages.error(request, 'This order can no longer be cancelled.')
        else:
            with transaction.atomic():
                for item in order.items.select_related('variant'):
                    variant = Variant.objects.select_for_update().get(pk=item.variant_id)
                    variant.stock += item.quantity
                    variant.save(update_fields=['stock'])
                order.status = Order.Status.CANCELLED
                order.save(update_fields=['status'])
            send_order_status_update(request, order)
            messages.success(request, f'Order #{order.id} has been cancelled.')

    return redirect('orders:detail', token=order.guest_token)


@login_required
def request_return(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.status != Order.Status.DELIVERED:
        messages.error(request, 'Returns can only be requested for delivered orders.')
        return redirect('orders:detail', token=order.guest_token)

    if order.return_requests.filter(status__in=['pending', 'approved']).exists():
        messages.info(request, 'You already have an open request for this order.')
        return redirect('orders:detail', token=order.guest_token)

    if request.method == 'POST':
        form = ReturnRequestForm(request.POST, order=order)
        if form.is_valid():
            return_request = form.save()
            send_return_request_received(request, return_request)
            messages.success(request, 'Your request has been submitted. We’ll get back to you shortly.')
            return redirect('orders:detail', token=order.guest_token)
    else:
        form = ReturnRequestForm(order=order)

    return render(request, 'orders/return_request.html', {'form': form, 'order': order})
