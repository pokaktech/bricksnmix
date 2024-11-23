from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid
from accounts.models import DeliveryAddress
from datetime import timedelta






class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    def __str__(self):
        return f"Cart - {self.user if self.user else self.session_id}"

        
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=now)  # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update on save

    def __str__(self):
        if self.cart.user:
            return f"{self.product.name} in {self.cart.user.username}'s Cart"
        else:
            return f"{self.product.name} in {self.cart.session_id}'s Cart"
           

   

class CustomerOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    net_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    order_number = models.CharField(max_length=100, unique=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE)
    
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    # is_canceled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


        

class OrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, related_name='items', on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ordered', 'Ordered'),## ordered_confirmed
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=50, choices=[('0', 'Pending'), ('1', 'Ordered'), ('2', 'Shipped'), ('3', 'Delivered')], default='1')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # is_approved = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=50, choices=[('COD', 'COD'), ('UPI', 'UPI'), ('CREDIT CARD', 'CREDIT CARD'), ('DEBIT CARD', 'DEBIT CARD')], default='COD')
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.IntegerField(default=7)  # Estimated delivery time in days
    delivered_at = models.DateField(null=True, blank=True)  # Actual delivery date

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def estimated_delivery_date(self):
        if self.delivered_at:
            # If the product is delivered, return the actual delivery date
            return self.delivered_at
        # Otherwise, calculate the estimated delivery date
        return self.order.created_at + timedelta(days=self.delivery_time)

class OrderProductImage(models.Model):
    order_item = models.ForeignKey(OrderItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='order_item_images/')

    def __str__(self):
        return f"Image for {self.order_item.product.name}"
    



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    

