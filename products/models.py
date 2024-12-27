from django.db import models

from categories.models import Category, Subcategory
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid






# class Banner(models.Model):
#     name = models.CharField(max_length=255)
#     image = models.ImageField(upload_to='banners/', blank=True, null=True)

#     def __str__(self):
#         return self.name
    
class Brand(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='brands/images/', blank=True, null=True)
    brand_banner = models.ImageField(upload_to='brands/banners/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return self.name    
    



class Banner(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banners')
    title = models.CharField(max_length=255)  # Offer title
    banner = models.ImageField(upload_to='banners/')  # Advertisement banner
    start_date = models.DateField()  # Offer start date
    end_date = models.DateField()  # Offer end date
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')  # Admin approval status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Special Offer by {self.seller.username} - {self.title}"


class BannerProduct(models.Model):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name='banner_products')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Assume Product model exists
    # discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Discount percentage for the product
    product_banner_image = models.ImageField(upload_to='banner_product_images/')

    def __str__(self):
        return f"{self.product.name} in {self.banner.title}"




class SpecialOffer(models.Model):
    # STATUS_CHOICES = [
    #     ('Pending', 'Pending'),
    #     ('Approved', 'Approved'),
    #     ('Rejected', 'Rejected'),
    # ]

    # seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='special_offers')
    title = models.CharField(max_length=255)  # Offer title
    banner = models.ImageField(upload_to='offer_banners/')  # Advertisement banner
    start_date = models.DateField()  # Offer start date
    end_date = models.DateField()  # Offer end date
    # status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')  # Admin approval status
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Special Offer by {self.title}"


class SpecialOfferProduct(models.Model):
    offer = models.ForeignKey(SpecialOffer, on_delete=models.CASCADE, related_name='offer_products')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='special_offer_products')
    special_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    original_price = None  # Temporary attribute to store original price (optional)

    def save(self, *args, **kwargs):
        # Backup the original price for restoration later
        if not hasattr(self.product, 'original_price'):
            self.product.original_price = self.product.price
        
        # Apply the special discount
        discounted_price = self.product.price * (1 - (self.special_discount_percentage / 100))
        self.product.price = round(discounted_price, 2)
        self.product.save()
        
        super(SpecialOfferProduct, self).save(*args, **kwargs)

    def revert_price(self):
        # Revert the product price to its original price
        if hasattr(self.product, 'original_price'):
            self.product.price = self.product.original_price
            self.product.save()

    def __str__(self):
        return f"{self.product.name} in {self.offer.title} - {self.special_discount_percentage}% off"




class Sponsored(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sponsored')
    title = models.CharField(max_length=255)
    sponsored_banner = models.ImageField(upload_to='sponsored_banners/')  # Advertisement banner
    start_date = models.DateField()  # Offer start date
    end_date = models.DateField()  # Offer end date
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')  # Admin approval status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sponsored by {self.seller.username} - {self.title}"


class SponsoredProduct(models.Model):
    sponsored = models.ForeignKey(Sponsored, on_delete=models.CASCADE, related_name='sponsored_products')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in {self.sponsored.title}"




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
    delivery_time = models.IntegerField(default=3)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    # product_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    stock = models.IntegerField(default=50)
    stock_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=now)  # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-update on save
    # images = models.JSONField(blank=True,null=True)


    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0

    def save(self, *args, **kwargs):
        # Automatically update stock_status based on stock value
        if self.stock == 0:
            self.stock_status = False
        # else:
        #     self.stock_status = True

        if self.actual_price and self.offer_percent:
            discount_amount = (self.actual_price * self.offer_percent) / 100
            self.price = self.actual_price - discount_amount
        else:
            self.price = self.actual_price  # No discount if offer_percent is None or 0
        super(Product, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name  
    



class Productimg(models.Model):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"  
    




class RatingReview(models.Model):
    # product_id = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product_id} - {self.user.username}'
    


class Wishlist(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Wishlist - {self.user if self.user else self.session_id}"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.wishlist.user:
            return f"{self.product.name} in {self.wishlist.user.username}'s Wishlist"
        else:
            return f"{self.product.name} in {self.wishlist.session_id}'s Wishlist"