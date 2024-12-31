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
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    session_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
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
    # bio = models.TextField(blank=True, null=True)
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
    
    date_update = models.DateTimeField(auto_now=True, blank=True, null=True)
    slug = models.SlugField(
        blank=True, null=True, allow_unicode=True, unique=True, verbose_name=_("Slugfiy"))

    phone = models.CharField(max_length=20, blank=True, null=True)
    default_address = models.ForeignKey('DeliveryAddress', null=True, blank=True, on_delete=models.SET_NULL)
    # gst = models.CharField(max_length=15, blank=True, null=True)
    # shopname = models.CharField(max_length=100, blank=True, null=True)
    # logoimage = models.ImageField(upload_to='logos/', blank=True, null=True)
    # company_name = models.CharField(max_length=100, blank=True, null=True)
    # latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
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

        

        super().save(*args, **kwargs)


def create_profile(sender, instance, created, **kwargs):
    if created and instance:
        Profile.objects.create(user=instance)


post_save.connect(create_profile, sender=User)




class Company(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    mail_id = models.EmailField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.vendor.username} and Company {self.name}"



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


    




class AppFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who gives the review
    rating = models.FloatField()
    review = models.TextField(blank=True, null=True)  # Review comments
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the review was created

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} stars"

    class Meta:
        ordering = ['-created_at']  # Show newest reviews first
