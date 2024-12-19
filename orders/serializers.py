from rest_framework import serializers
from .models import Cart, CartItem, OrderItem, OrderProductImage, CustomerOrder, Notification








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
        fields = ['product', 'status', 'quantity', 'price', 'images']

class CustomerOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = CustomerOrder
        fields = ['total_price', 'delivery_charge', 'net_total', 
                  'order_number', 'delivery_address', 'tracking_number', 
                  'carrier', 'items']
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'heading', 'message', 'is_read', 'created_at']


class SellerOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    amount = serializers.CharField(source='price')
    state = serializers.CharField(source='get_status_display')
    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'quantity', 'amount', 'status', 'state']


