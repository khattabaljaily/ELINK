from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Variant

from .models import CartItem
from .serializers import CartSerializer
from .utils import get_cart


class CartDetailView(APIView):
    def get(self, request):
        cart = get_cart(request)
        return Response(CartSerializer(cart).data)


class CartAddItemView(APIView):
    def post(self, request):
        cart = get_cart(request)
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))
        variant = get_object_or_404(Variant, pk=variant_id)

        if quantity < 1:
            return Response({'detail': 'Quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)
        if variant.stock < quantity:
            return Response({'detail': 'Not enough stock available.'}, status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartUpdateItemView(APIView):
    def post(self, request, item_id):
        cart = get_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        quantity = int(request.data.get('quantity', 1))

        if quantity < 1:
            return Response({'detail': 'Quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)
        if item.variant.stock < quantity:
            return Response({'detail': 'Not enough stock available.'}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = quantity
        item.save()
        return Response(CartSerializer(cart).data)


class CartRemoveItemView(APIView):
    def post(self, request, item_id):
        cart = get_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        return Response(CartSerializer(cart).data)
