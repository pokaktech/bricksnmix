from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from PIL import Image
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from .utils import code_generator, create_shortcode
from datetime import timedelta
from django.utils.timezone import now
import uuid




class TemporaryUserContact(models.Model):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



class SuperAdmin(models.Model):
    purpose = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.phone_number} ({self.purpose})"


class Profile(models.Model):
    image = models.ImageField(
        upload_to='profile_pic/', blank=True, null=True, )
    user = models.OneToOneField(    
        User, on_delete=models.CASCADE)
    # display_name = models.CharField(max_length=100, blank=True, null=True, )
    bio = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=100, blank=True, null=True, )
    address = models.CharField(max_length=100, blank=True, null=True, )
    city = models.CharField(max_length=100, blank=True, null=True, )
    post_code = models.CharField(max_length=100, blank=True, null=True, )
    country = models.CharField(max_length=100, blank=True, null=True, )
    state = models.CharField(max_length=100, blank=True, null=True, )

    customer = 'customer'
    seller = 'seller'
    account_select = [
        (customer, 'customer'),
        (seller, 'seller'),
    ]
    user_type = models.CharField(
        max_length=13,
        choices=account_select,
        default=customer,
        blank=True, null=True,
    )
    # admission = models.BooleanField(default=False, verbose_name=_("admission") , blank=True, null=True)
    # code = models.CharField(max_length=250, blank=True, null=True)
    # recommended_by = models.ForeignKey(
    #     User, on_delete=models.CASCADE, related_name="recommended_by", blank=True, null=True)
    # referrals = models.IntegerField(default=0, blank=True, null=True)
    # blance = models.FloatField(default=0.00, blank=True, null=True)
    # requested = models.FloatField(default=0.00, blank=True, null=True)
    # date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_update = models.DateTimeField(auto_now=True, blank=True, null=True)
    slug = models.SlugField(
        blank=True, null=True, allow_unicode=True, unique=True, verbose_name=_("Slugfiy"))

    # email = models.EmailField(max_length=254, blank=True, null=True)
    # name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    default_address = models.ForeignKey('DeliveryAddress', null=True, blank=True, on_delete=models.SET_NULL)
    # type = models.CharField(max_length=10, choices=[('user', 'User'), ('seller', 'Seller')], blank=True, null=True)
    gst = models.CharField(max_length=15, blank=True, null=True)
    shopname = models.CharField(max_length=100, blank=True, null=True)
    logoimage = models.ImageField(upload_to='logos/', blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return self.user.username if self.user else "No User"

    # def save(self, *args, **kwargs):
    #     return super().save(*args, **kwargs)

    def get_recommended_profiles(self):
        qs = Profile.objects.all()
        my_recs = []
        for profile in qs:
            if profile.recommended_by == self.user:
                my_recs.append(profile)
        return my_recs

    def save(self, *args, **kwargs):
        if not self.slug or self.slug is None or self.slug == "":
            self.slug = slugify(self.user.username, allow_unicode=True)
            qs_exists = Profile.objects.filter(
                slug=self.slug).exists()
            if qs_exists:
                self.slug = create_shortcode(self)

        # if self.code is None or self.code == "":
        #     # code = generate_ref_code()
        #     # self.code = code
        #     self.code = f'{self.user}'

        # img = Image.open(self.image.path)
        # if img.width > 300 or img.height > 300:
        #     out_size = (300, 300)
        #     img.thumbnail(out_size)
        #     img.save(self.image.path)

        super().save(*args, **kwargs)


def create_profile(sender, instance, created, **kwargs):
    if created and instance:
        Profile.objects.create(user=instance)


post_save.connect(create_profile, sender=User)



class BankAccount(models.Model):
    vendor_profile = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True, )
    account_number = models.CharField(max_length=200, blank=True, null=True, )
    swift_code = models.CharField(max_length=200, blank=True, null=True, )
    account_name = models.CharField(max_length=200, blank=True, null=True, )
    country = models.CharField(max_length=200, blank=True, null=True, )
    paypal_email = models.CharField(max_length=200, blank=True, null=True, )
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_update = models.DateTimeField(auto_now=True, blank=True, null=True)

    # def __str__(self):
    #      return str(self.account_number)



class SocialLink(models.Model):
    vendor_profile = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, blank=True, null=True)
    facebook = models.CharField(max_length=200, blank=True, null=True, )
    twitter = models.CharField(max_length=200, blank=True, null=True, )
    instagram = models.CharField(max_length=200, blank=True, null=True, )
    pinterest = models.CharField(max_length=200, blank=True, null=True, )


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Subcategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class Banner(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='brands/', blank=True, null=True)

    def __str__(self):
        return self.name    

class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    # image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    min_order_quantity = models.IntegerField(default=50)
    min_order_quantity_two = models.IntegerField(default=100)
    min_order_quantity_three = models.IntegerField(default=150)
    min_order_quantity_four = models.IntegerField(default=200)
    min_order_quantity_five = models.IntegerField(default=250)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    product_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    stock = models.IntegerField(default=0)
    stock_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)  # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update on save
    # images = models.JSONField(blank=True,null=True)

    def save(self, *args, **kwargs):
        # Automatically update stock_status based on stock value
        if self.stock == 0:
            self.stock_status = False
        # else:
        #     self.stock_status = True
        super(Product, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name    
    
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
           
class Productimg(models.Model):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"    

# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='product_images/')

#     def __str__(self):
#         return f"Image for {self.product.name

class RatingReview(models.Model):
    # product_id = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product_id} - {self.user.username}'

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=25)
    housename = models.CharField(max_length=255)
    # place = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    # country = models.CharField(max_length=100)
    pincode = models.IntegerField(default=0)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=now)  # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update on save
    # is_default = models.BooleanField(default=False)
    # latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"

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
    
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s Wishlist"




