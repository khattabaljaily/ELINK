from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.utils import get_cart
from payments.registry import get_gateway

from .forms import CheckoutForm
from .models import Order, OrderItem


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
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.save()

                for item in cart.items.select_related('variant__product'):
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        product_name=item.variant.product.name,
                        variant_label=' / '.join(p for p in (item.variant.size, item.variant.color) if p),
                        unit_price=item.variant.price,
                        quantity=item.quantity,
                    )
                    item.variant.stock = max(item.variant.stock - item.quantity, 0)
                    item.variant.save(update_fields=['stock'])

                order.recalculate_total()

                gateway = get_gateway(form.cleaned_data['payment_method'])
                gateway.initiate_payment(order)

                cart.items.all().delete()

            return redirect('orders:confirmation', order_id=order.pk)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


def confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/confirmation.html', {'order': order})


def order_detail(request, order_id):
    lookup = {'pk': order_id}
    if request.user.is_authenticated:
        lookup['user'] = request.user
    order = get_object_or_404(Order, **lookup)
    return render(request, 'orders/detail.html', {'order': order})
