from rest_framework import serializers
from .models import *




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
        fields = [ 'id', 'brandname', 'image']  
        read_only_fields = ['id']      




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




class ProductimgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productimg
        fields = ['id','image']




class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductimgSerializer(many=True, required=False)
    wishlisted = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()
    product_review_count = serializers.SerializerMethodField()
    # image = serializers.ImageField(required=False)
    
    class Meta:
        model = Product
        fields = ['id', 'vendor', 'category', 'subcategory', 'brand', 'name', 'price', 'offer_percent', 'actual_price', 'description', 'product_rating', 'product_review_count', 'stock', 'stock_status', 'min_order_quantity', 'min_order_quantity_two', 'min_order_quantity_three', 'min_order_quantity_four', 'min_order_quantity_five', 'delivery_charge', 'delivery_time', 'product_images', 'wishlisted', 'created_at', 'updated_at']
        read_only_fields = ['price', 'product_rating', 'created_at', 'updated_at']

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
    
    def get_wishlisted(self, obj):
        request = self.context.get('request')
        if request is None:
            return False

        user = request.user if request.user.is_authenticated else None
        # session_id = request.session.session_key
        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            session_id = request.session.session_key
        print("Session_id", session_id)

        # Check if the product is wishlisted for authenticated users
        if user:
            wishlist = Wishlist.objects.filter(user=user).first()
        else:
            # Check by session ID if the user is not authenticated
            wishlist = Wishlist.objects.filter(session_id=session_id).first()

        # If a wishlist exists, check if the product is in it
        if wishlist:
            return WishlistItem.objects.filter(wishlist=wishlist, product=obj).exists()

        return False
    
    def get_product_rating(self, obj):
        return obj.get_average_rating()
    def get_product_review_count(self, obj):
        return obj.reviews.count()
    


class CustomerSpecialOfferProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOfferProduct
        fields = ['product', 'discount_percentage', 'product_offer_image']

class CustomerSpecialOfferSerializer(serializers.ModelSerializer):
    offer_products = CustomerSpecialOfferProductSerializer(many=True)

    class Meta:
        model = SpecialOffer
        fields = ['title', 'banner', 'start_date', 'end_date', 'offer_products']




class RatingReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = RatingReview
        fields = ['id', 'product', 'rating', 'comments', 'username', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']



class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['id', 'product']

class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items']