
from rest_framework import serializers
# from .models import Product
from .models import Product, ProductSize, ProductImage, ProductRating

# class ProductDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'  # Or specify the fields you want to include


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    product_variations = ProductSizeSerializer(many=True, source='productsize_set')
    product_images = ProductImageSerializer(many=True, source='productimage_set')
    product_ratings = ProductRatingSerializer(many=True, source='productrating_set')

    class Meta:
        model = Product
        fields = '__all__'