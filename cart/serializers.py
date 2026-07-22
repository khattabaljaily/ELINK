from rest_framework import serializers

from products.serializers import VariantSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'variant', 'product_name', 'quantity', 'subtotal')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'total_items')
