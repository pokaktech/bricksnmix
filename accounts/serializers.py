from rest_framework import serializers
from .models import DeliveryAddress
from django.contrib.auth.models import User
from .models import *
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


# class ProfileSerializer(serializers.ModelSerializer):
#     # full_name = serializers.SerializerMethodField()
#     username = serializers.CharField(source='user.username')
#     email = serializers.CharField(source='user.email')
#     class Meta:
#         fields = ['username', 'mobile_number', 'email', 'address', 'post_code', 'city', 'state', 'country']
#         model = Profile
#         # exclude = ['id',]
#     # def get_full_name(self, obj):
#     #     return f"{obj.user.first_name} {obj.user.last_name}"



class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    # full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email')  # Make the email editable through user

    class Meta:
        fields = ['username', 'mobile_number', 'email', 'address', 'post_code', 'city', 'state', 'country']
        model = Profile

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def update(self, instance, validated_data):
        # Update the user instance (email and other fields)
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()

        # Update the profile instance
        return super().update(instance, validated_data)


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
    

# class SellerSignupSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'confirm_password']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise ValidationError("Passwords do not match")
#         return data

#     def create(self, validated_data):
#         # Remove confirm_password as it's not needed for creating the User
#         validated_data.pop('confirm_password')

#         # Create the user
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )

#         # Automatically set the Profile's user_type to 'seller'
#         user.profile.user_type = Profile.seller
#         user.profile.save()

#         return user
    




class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'location', 'mail_id', 'logo']


class SellerSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    company = CompanySerializer()  # Nested serializer to capture company details

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'company']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, data):
        # Ensure passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Extract and remove company details
        company_data = validated_data.pop('company')
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

        # Create the company and associate it with the vendor (user)
        Company.objects.create(vendor=user, **company_data)

        return user
    


class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        fields = ['user', 'rating', 'review', 'created_at']
        read_only_fields = ['user', 'created_at']  # User and created_at should be read-only

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value