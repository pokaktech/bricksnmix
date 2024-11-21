from rest_framework import serializers
from .models import Category, Subcategory
from .models import CategoryBanner










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


class CategoryBannerSerializer(serializers.ModelSerializer):
    bannername = serializers.CharField(source='name')
    image = serializers.ImageField()

    class Meta:
        model = CategoryBanner
        fields = ['id', 'bannername', 'image']