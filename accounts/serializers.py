from rest_framework import serializers
from .models import DeliveryAddress
from django.contrib.auth.models import User
from .models import BankAccount, Profile
from .models import SocialLink
from rest_framework.exceptions import ValidationError

# class SubcategorySerializer(serializers.ModelSerializer):
#     id = serializers.CharField(source='pk')
#     subcategoryname = serializers.CharField(source='name')
#     image = serializers.ImageField()

#     class Meta:
#         model = Subcategory
#         fields = ['id', 'subcategoryname', 'image']

# class CategorySerializer(serializers.ModelSerializer):
#     id = serializers.CharField(source='pk')
#     categoryname = serializers.CharField(source='name')
#     image = serializers.ImageField()
#     Subcategory = SubcategorySerializer(many=True, source='subcategories')

#     class Meta:
#         model = Category
#         fields = ['id', 'categoryname', 'image', 'Subcategory']


        
       
        


# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = ['image']

# class ProductDetailSerializer(serializers.ModelSerializer):
#     Categoryid = serializers.CharField(source='category.id')
#     Productid = serializers.CharField(source='pk')
#     Price = serializers.DecimalField(max_digits=10, decimal_places=2)
#     Offerpercent = serializers.DecimalField(max_digits=5, decimal_places=2)
#     Actualprice = serializers.DecimalField(max_digits=10, decimal_places=2)
#     Image = ProductImageSerializer(source='images', many=True)
#     Description = serializers.CharField(source='description')
#     product_rating = serializers.DecimalField(max_digits=3, decimal_places=2)

#     class Meta:
#         model = Product
#         fields = ['id', 'Categoryid', 'Productid', 'name', 'Price', 'Offerpercent', 'Actualprice', 'Image', 'Description', 'product_rating']        



    
  



class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'name', 'mobile', 'housename', 'state', 'city', 'landmark', 'pincode', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')









class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['id', 'user']
class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'


class CustomerSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Remove confirm_password as it's not needed for creating the User
        validated_data.pop('confirm_password')

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Automatically set the Profile's user_type to 'customer'
        user.profile.user_type = Profile.customer
        user.profile.save()

        return user
    

class SellerSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Remove confirm_password as it's not needed for creating the User
        validated_data.pop('confirm_password')

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Automatically set the Profile's user_type to 'seller'
        user.profile.user_type = Profile.seller
        user.profile.save()

        return user
    


