from django.shortcuts import get_object_or_404

from categories.models import Category, CategoryBanner, Subcategory
from categories.serializers import *

from products.models import Product
from products.serializers import ProductSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status









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
    

class CustomerCategoryDetailtView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response({
                'Status': '1',
                'message': 'Category details fetched successfully',
                'Data': [serializer.data]
            })
        except Category.DoesNotExist:
            return Response({
                'Status': '0',
                'message': 'Category not found',
                'Data': None
            }, status=404)



class CustomerCategoryProductView(APIView):
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
        product_serializer = ProductSerializer(products, many=True, context={'request': request})

        # Return category and products
        return Response({
            'Status': '1',
            'message': 'Category details fetched successfully',
            'Data': product_serializer.data
                # 'category': CustomerCategorySerializer(category).data,
            
        })
    



# Get all subcategories
class CustomerSubCategoryListView(generics.ListAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)

        return Response({
            'Status': '1',
            'message': 'SubCategories fetched successfully',
            'Data': serializer.data
        })
    

# Get all products under a subcategory
class CustomerSubCategoryProductView(APIView):
    def get(self, request, pk):
        try:
            subcategory = Subcategory.objects.get(pk=pk)
        except Subcategory.DoesNotExist:
            return Response({
                'Status': '0',
                'message': 'Category not found',
                'Data': None
            }, status=404)

        # Get products associated with the category
        products = Product.objects.filter(subcategory=subcategory)
        product_serializer = ProductSerializer(products, many=True, context={'request': request})

        # Return category and products
        return Response({
            'Status': '1',
            'message': 'SubCategory details fetched successfully',
            'Data': product_serializer.data
                # 'category': CustomerCategorySerializer(category).data,
            
        })
    


#Pass category id to get all sub categories under that category
class CustomerCategorySubCategoryView(APIView):
    # def get_object(self, category_id):
    #     try:
    #         return Category.objects.get(id=category_id)
    #     except Category.DoesNotExist:
    #         return None

    def get(self, request, category_id, format=None):
        category = Category.objects.get(id=category_id)
        if category is None:
            return Response({"Status": "0", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            subcategory = Subcategory.objects.filter(category=category)
            serializer = SubcategorySerializer(subcategory, many=True)
            return Response({
                "Status": "1",
                "message": "Success",
                "Data": serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({"Status": "0", "message": "No subcategories for this category"})


class CategoryProductSearchView(APIView):
    def post(self, request, category_id):
        search_word = request.data.get('search_word', '')
        if search_word:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category, name__icontains=search_word)
            serializer = ProductSerializer(products, many=True, context={'request': request})
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
