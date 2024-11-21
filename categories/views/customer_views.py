from django.shortcuts import get_object_or_404

from categories.models import Category, CategoryBanner
from categories.serializers import CategoryBannerSerializer, CustomerCategorySerializer

from products.models import Product
from products.serializers import ProductSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics










class CustomerCategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CustomerCategorySerializer

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)

        return Response({
            'Status': '1',
            'message': 'Categories fetched successfully',
            'Data': serializer.data
        })

class CustomerCategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({
                'Status': '0',
                'message': 'Category not found',
                'Data': None
            }, status=404)

        # Get products associated with the category
        products = Product.objects.filter(category=category)
        product_serializer = ProductSerializer(products, many=True)

        # Return category and products
        return Response({
            'Status': '1',
            'message': 'Category details fetched successfully',
            'Data': product_serializer.data
                # 'category': CustomerCategorySerializer(category).data,
            
        })
    


class CategoryProductSearchView(APIView):
    def post(self, request, category_id):
        search_word = request.data.get('search_word', '')
        if search_word:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category, name__icontains=search_word)
            serializer = ProductSerializer(products, many=True)
            return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data})
        return Response({'Status': '0', 'message': 'Search word not provided'})
    





class CategoryBannerView(APIView):
    def get(self, request, format=None):
        print("check")
        category_banners = CategoryBanner.objects.all()
        serializer = CategoryBannerSerializer(category_banners, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })  
