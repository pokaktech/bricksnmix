# from django.db import models
# from django.contrib.auth.models import User
# from products.models import Product
# from django.core.validators import MinValueValidator, MaxValueValidator
# from accounts.models import Profile
# from django.utils.safestring import mark_safe
# from django.utils.translation import ugettext_lazy as _
# from django_countries.fields import CountryField

# # from localflavor.us.models import USStateField

# # Create your models here.


# class Order(models.Model):
#     user = models.ForeignKey(
#         User, on_delete=models.SET_NULL, related_name='user_client',  blank=True, null=True)
#     email_client = models.EmailField(
#         max_length=250,  blank=True, null=True)
#     #vendors = models.ManyToManyField(Profile, related_name='vendors')
#     order_date = models.DateTimeField(auto_now_add=True)
#     date_update = models.DateTimeField(auto_now=True)
#     details = models.ManyToManyField(Product, through="OrderDetails")
#     coupon = models.ForeignKey(
#         "Coupon", on_delete=models.SET_NULL, blank=True, null=True)
#     sub_total = models.CharField(max_length=50,  blank=True, null=True)
#     discount = models.CharField(max_length=50,  blank=True, null=True)
#     shipping = models.CharField(max_length=50,  blank=True, null=True)
#     amount = models.CharField(max_length=50, )
#     tracking_no = models.CharField(max_length=50,  blank=True, null=True)
#     rpt_cache = models.URLField(blank=True, null=True)
#     weight = models.DecimalField(
#         default=0,  max_digits=10, decimal_places=3,  verbose_name=_("WEIGHT"))
#     is_finished = models.BooleanField(default=False)
#     PENDING = 'PENDING'
#     Underway = 'Underway'
#     COMPLETE = 'COMPLETE'
#     Refunded = 'Refunded'
#     Status_select = [
#         (PENDING, 'PENDING'),
#         (Underway, 'Underway'),
#         (COMPLETE, 'COMPLETE'),
#         (Refunded, 'Refunded'),
#     ]
#     status = models.CharField(
#         max_length=13,
#         choices=Status_select,
#         default=PENDING,
#     )

#     merchant_order_id = models.CharField(
#         max_length=100,  blank=True, null=True)

#     order_id_paymob = models.CharField(max_length=100,  blank=True, null=True)

#     auth_token_order = models.TextField(blank=True, null=True)
#     trnx_id = models.CharField(max_length=100,  blank=True, null=True)

#     def __str__(self):
#         # return f"Order ID:{self.id}-{self.user}-{self.user.email}-{self.status}"
#         # return f"Order ID:{self.id}"
#         return str(self.id)

#     # def get_recommended_profiles(self):
#     #     qs = Profile.objects.all()
#     #     my_recs = []
#     #     for profile in qs:
#     #         if profile.recommended_by == self.user:
#     #             my_recs.append(profile)
#     #     return my_recs

#     def save(self, *args, **kwargs):
#         if self.status == "PENDING":
#             order_suppliers = OrderSupplier.objects.all().filter(order=self.id)
#             for order_supplier in order_suppliers:
#                 order_supplier.status = self.status
#                 order_supplier.save()

#         else:
#             order_suppliers = OrderSupplier.objects.all().filter(order=self.id)
#             for order_supplier in order_suppliers:
#                 order_supplier.status = self.status
#                 order_supplier.is_finished = True
#                 order_supplier.save()

#             ref = float(self.amount)*0.025
#             try:
#                 recommended_by = Profile.objects.get(
#                     user=self.user).recommended_by
#                 blance = Profile.objects.get(user=recommended_by)
#                 blance.blance = blance.blance + float(ref)
#                 blance.save()
#             except:
#                 pass

#         super().save(*args, **kwargs)

#     class Meta:
#         ordering = ('-id',)


# class OrderDetails(models.Model):
#     supplier = models.ForeignKey(
#         User, on_delete=models.SET_NULL, related_name='user_supplier', blank=True, null=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     quantity = models.IntegerField()
#     size = models.CharField(max_length=10,  blank=True, null=True)
#     weight = models.DecimalField(
#         default=0,  max_digits=10, decimal_places=3,  verbose_name=_("WEIGHT"))

#     def __str__(self):
#         return f"Order Details ID:{self.id}-user:{self.order.user}-product id:{self.product.id}-order id:{self.order.id}"

#     class Meta:
#         ordering = ('-id',)

#     def order_photo(self):
#         return mark_safe('<img src="{}" width="100" />'.format(self.product.PRDImage.url))
#     order_photo.short_description = "image"
#     order_photo.allow_tags = True

#     # def save(self, *args, **kwargs):

#     #     super().save(*args, **kwargs)


# class Coupon(models.Model):
#     code = models.CharField(max_length=50, unique=True)
#     valid_form = models.DateTimeField()
#     valid_to = models.DateTimeField()
#     discount = models.PositiveIntegerField(
#         validators=[MinValueValidator(0), MaxValueValidator(100)])
#     active = models.BooleanField()

#     class Meta:
#         # verbose_name = "Coupons"
#         # verbose_name_plural = "Couponss"
#         ordering = ('-id',)

#     def __str__(self):
#         return f"{self.code}"


# class Payment(models.Model):
#     order = models.ForeignKey(
#         Order, on_delete=models.CASCADE,  blank=True, null=True)
#     # order_supplier = models.ForeignKey(
#     #     "OrderSupplier", on_delete=models.CASCADE,  blank=True, null=True)
#     first_name = models.CharField(max_length=100,)
#     last_name = models.CharField(max_length=100, )
#     # country = models.ForeignKey(
#     #     Country, on_delete=models.SET_NULL, blank=True, null=True)
#     country = models.CharField(max_length=100, blank=True, null=True)
#     country_code = models.CharField(max_length=100, blank=True, null=True)
#     # state = models.ForeignKey(
#     #     State, on_delete=models.SET_NULL, blank=True, null=True)
#     state = models.CharField(max_length=100, blank=True, null=True)
#     street_address = models.CharField(max_length=100,)
#     post_code = models.CharField(max_length=10, )
#     # by_blance = models.CharField(max_length=100, )
#     City = models.CharField(max_length=100, )
#     Email_Address = models.EmailField()
#     phone = models.CharField(max_length=20, )
#     payment_method = models.CharField(max_length=100, )

#     def __str__(self):
#         return f"Payment ID:{self.id}- order:{self.order}"

#     class Meta:
#         ordering = ('-id',)


# class Country(models.Model):
#     name_country = models.CharField(max_length=40)
#     country_code = models.CharField(max_length=40)
#     countries = CountryField()

#     def __str__(self):
#         return self.name_country

#     class Meta:
#         ordering = ('name_country',)


# class OrderSupplier(models.Model):
#     user = models.ForeignKey(
#         User, on_delete=models.SET_NULL,  blank=True, null=True)
#     email_client = models.EmailField(
#         max_length=250,  blank=True, null=True)
#     vendor = models.ForeignKey(
#         Profile, on_delete=models.SET_NULL, related_name='vendors', blank=True, null=True)
#     order = models.ForeignKey(
#         Order, on_delete=models.CASCADE, blank=True, null=True)
#     order_date = models.DateTimeField(auto_now_add=True)
#     date_update = models.DateTimeField(auto_now=True)
#     coupon = models.ForeignKey(
#         Coupon, on_delete=models.SET_NULL, blank=True, null=True)
#     sub_total = models.CharField(max_length=50,  blank=True, null=True)
#     discount = models.CharField(max_length=50,  blank=True, null=True)
#     shipping = models.CharField(max_length=50,  blank=True, null=True)
#     amount = models.CharField(max_length=50, )
#     # tracking_no = models.CharField(max_length=50,  blank=True, null=True)
#     # rpt_cache = models.URLField(blank=True, null=True)
#     weight = models.DecimalField(
#         default=0,  max_digits=10, decimal_places=3,  verbose_name=_("WEIGHT"))
#     is_finished = models.BooleanField(default=False)
#     PENDING = 'PENDING'
#     Underway = 'Underway'
#     COMPLETE = 'COMPLETE'
#     Refunded = 'Refunded'
#     Status_select = [
#         (PENDING, 'PENDING'),
#         (Underway, 'Underway'),
#         (COMPLETE, 'COMPLETE'),
#         (Refunded, 'Refunded'),
#     ]
#     status = models.CharField(
#         max_length=13,
#         choices=Status_select,
#         default=PENDING,
#     )

#     def __str__(self):

#         return str(self.id)

#     def save(self, *args, **kwargs):

#         if self.status == "Underway":
#             ref = float(self.amount)*0.025
#             try:
#                 recommended_by = Profile.objects.get(
#                     user=self.user).recommended_by
#                 blance = Profile.objects.get(user=recommended_by)
#                 blance.blance = blance.blance + float(ref)
#                 blance.save()
#             except:
#                 pass
#         super().save(*args, **kwargs)

#     class Meta:
#         ordering = ('-id',)


# class OrderDetailsSupplier(models.Model):
#     supplier = models.ForeignKey(
#         User, on_delete=models.SET_NULL,  blank=True, null=True)
#     product = models.ForeignKey(
#         Product, on_delete=models.SET_NULL, blank=True, null=True)
#     order = models.ForeignKey(
#         Order, on_delete=models.CASCADE, blank=True, null=True)
#     order_supplier = models.ForeignKey(
#         OrderSupplier, on_delete=models.CASCADE,   blank=True, null=True)
#     order_details = models.ForeignKey(
#         OrderDetails, on_delete=models.CASCADE, blank=True, null=True)
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     quantity = models.IntegerField()
#     size = models.CharField(max_length=10,  blank=True, null=True)
#     weight = models.DecimalField(
#         default=0,  max_digits=10, decimal_places=3,  verbose_name=_("WEIGHT"))

#     def __str__(self):
#         return f"Order Details ID:{self.id}-user:{self.order.user}-product id:{self.product.id}-order id:{self.order.id}"

#     class Meta:
#         ordering = ('-id',)

#     def order_photo(self):
#         return mark_safe('<img src="{}" width="100" />'.format(self.product.PRDImage.url))
#     order_photo.short_description = "image"
#     order_photo.allow_tags = True

#     # def save(self, *args, **kwargs):
#     #     order_details = OrderDetails.objects.all().filter(order=self.order , supplier = self.supplier)
#     #     print(order_details)
#     #     f_total = 0
#     #     w_total = 0
#     #     for sub in order_details:
#     #         f_total += sub.price * sub.quantity
#     #         w_total += sub.weight * sub.quantity
#     #         total = f_total
#     #         weight = w_total
#     #     obj_order_supplier = OrderSupplier.objects.get(
#     #         id=self.order_supplier.id)
#     #     obj_order_supplier.amount = total
#     #     obj_order_supplier.save()
#     #     super().save(*args, **kwargs)












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
    # session_id = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True)
    session_id = models.CharField(max_length=40, unique=True, null=True, blank=True)

    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # quantity = models.IntegerField(default=1)
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
    # STATUS_CHOICES = [
    #     ('Ordered', 'Ordered'),
    #     ('Shipped', 'Shipped'),
    #     ('Delivered', 'Delivered'),
    #     ('CANCELLED', 'Cancelled'),
    # ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # status = models.CharField(max_length=50, choices=[('1', 'Ordered'), ('2', 'Shipped'), ('3', 'Delivered')], default='1')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    net_total = models.DecimalField(max_digits=10, decimal_places=2)
    # payment_type = models.CharField(max_length=50, blank=True, null=True)
    payment_type = models.CharField(max_length=50, choices=[('COD', 'COD'), ('UPI', 'UPI'), ('CREDIT CARD', 'CREDIT CARD'), ('DEBIT CARD', 'DEBIT CARD')], default='COD')
    order_number = models.CharField(max_length=100, unique=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True)
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    is_canceled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, related_name='items', on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),## ordered_confirmed
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=50, choices=[('0', 'Ordered'), ('1', 'Shipped'), ('2', 'Delivered')], default='1')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
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
    

