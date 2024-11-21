from rest_framework import serializers
from .models import Cart, CartItem, OrderItem, OrderProductImage, CustomerOrder








class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']


class OrderProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProductImage
        fields = ['image']





class OrderItemSerializer(serializers.ModelSerializer):
    images = OrderProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'status', 'is_approved', 'quantity', 'price', 'images']

class CustomerOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = CustomerOrder
        fields = ['total_price', 'delivery_charge', 'net_total', 'payment_type', 
                  'order_number', 'delivery_address', 'payment_status', 'tracking_number', 
                  'carrier', 'is_canceled', 'items']