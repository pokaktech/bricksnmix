from rest_framework import serializers
from .models import Category, Subcategory, Banner, Brand, Product, Productimg, RatingReview,Cart, CartItem, CustomerOrder, OrderItem, DeliveryAddress, OrderProductImage
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

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'category', 'name', 'image']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'subcategories']

class CustomerCategorySerializer(serializers.ModelSerializer):
    # subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image']
        
class BannerSerializer(serializers.ModelSerializer):
    bannername = serializers.CharField(source='name')
    image = serializers.ImageField()

    class Meta:
        model = Banner
        fields = ['id', 'bannername', 'image']        
        # extra_kwargs = {
        #     'id': {'read_only': True},
        #     'image': {'required': True}
        # }
        read_only_fields = ['id'] 
class BrandSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(required=True)
    brandname = serializers.CharField(source='name')
    image = serializers.ImageField()

    class Meta:
        model = Brand
        fields = [ 'brandname', 'image']        


class OfferProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    category = serializers.IntegerField(source='category.id')
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    offer_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    actual_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'price', 'offer_percent', 'actual_price']        
        


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
class ProductimgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productimg
        fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductimgSerializer(many=True, required=False)
    # image = serializers.ImageField(required=False)
    
    class Meta:
        model = Product
        fields = ['id', 'vendor', 'category', 'subcategory', 'brand', 'name', 'price', 'offer_percent', 'actual_price', 'description', 'stock', 'stock_status', 'min_order_quantity', 'delivery_charge', 'product_images']
        read_only_fields = ['product_rating']

    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        print(images_data)
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            Productimg.objects.create(product=product, image=image_data)
        return product
    
    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images', [])
        
        # Update product fields
        instance = super().update(instance, validated_data)
        
        # Handle updating or adding images
        if images_data:
            for image_data in images_data:
                Productimg.objects.create(product=instance, image=image_data)
        
        return instance
    
class RatingReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = RatingReview
        fields = '__all__'
        read_only_fields = ('created_at',)  

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'name', 'mobile', 'housename', 'state', 'city', 'landmark', 'pincode']

class OrderProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProductImage
        fields = ['image']

# class OrderItemSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'order', 'product', 'quantity', 'price', 'images']

class OrderItemSerializer(serializers.ModelSerializer):
    images = OrderProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'images']

# class CustomerOrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerOrder
#         fields = ['id', 'status', 'total_price', 'delivery_charge', 'net_total', 'payment_type', 'delivery_address', 'created_at', 'updated_at']


class CustomerOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = CustomerOrder
        fields = ['status', 'total_price', 'delivery_charge', 'net_total', 'payment_type', 
                  'order_number', 'delivery_address', 'payment_status', 'tracking_number', 
                  'carrier', 'is_canceled', 'items']
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