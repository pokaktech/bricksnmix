from rest_framework import serializers
from .models import Category, Subcategory, Banner, Brand, Product, Productimg, RatingReview,Cart, CartItem, CustomerOrder, OrderItem, DeliveryAddress, ProductImage
from django.contrib.auth.models import User
from .models import BankAccount, Profile
from .models import SocialLink
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
        fields = ['id', 'name', 'image']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'subcategories']
        
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
    id = serializers.CharField(source='pk')
    Categoryid = serializers.CharField(source='category.id')
    Productid = serializers.CharField(source='pk')
    name = serializers.CharField()
    Price = serializers.DecimalField(max_digits=10, decimal_places=2)
    Offerpercent = serializers.DecimalField(max_digits=5, decimal_places=2)
    actualprice = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.ImageField()

    class Meta:
        model = Product
        fields = ['id', 'Categoryid', 'Productid', 'name', 'Price', 'Offerpercent', 'actualprice', 'image']        
        


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
    images = ProductimgSerializer(many=True, required=False)
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'price', 'offer_percent', 'actual_price', 'image', 'description', 'product_rating', 'stock','images']

    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            Productimg.objects.create(product=product, image=image_data)
        return product
    
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
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class OrderItemSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price', 'images']

class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrder
        fields = ['id', 'user', 'status', 'total_price', 'delivery_charge', 'net_total', 'payment_type', 'delivery_address', 'created_at', 'updated_at']
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'
