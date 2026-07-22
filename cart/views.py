from django.shortcuts import render

from .utils import get_cart


def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})
