from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from categories.models import Category, Subcategory
from categories.serializers import CategorySerializer, SubcategorySerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics









@method_decorator(csrf_exempt, name='dispatch')
class CategoryListCreateView(APIView):
    """
    Handles both GET (list all categories) and POST (create a new category) requests.
    """
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Category added successfully",
                "Data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Status": "0",
            "message": "Failed to add category",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CategoryRetrieveUpdateDestroyAPIView(APIView):
    """
    Handles GET (retrieve), PUT/PATCH (update), and DELETE (remove) requests for a single category.
    """
    def get_object(self, category_id):
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None

    def get(self, request, category_id, format=None):
        category = self.get_object(category_id)
        if category is None:
            return Response({"Status": "0", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": [serializer.data]
        }, status=status.HTTP_200_OK)

    def put(self, request, category_id, format=None):
        category = self.get_object(category_id)
        if category is None:
            return Response({"Status": "0", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Category updated successfully",
                "Data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "Status": "0",
            "message": "Failed to update category",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id, format=None):
        category = self.get_object(category_id)
        if category is None:
            return Response({"Status": "0", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response({"Status": "1", "message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
# class SubcategoryListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Subcategory.objects.all()
#     serializer_class = SubcategorySerializer

# class SubcategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Subcategory.objects.all()
#     serializer_class = SubcategorySerializer   

#overwrite below for custom response
class SubcategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': '1',
            'message': 'Success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'status': '1',
                'message': 'Subcategory created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': '0',
            'message': 'Failed to create subcategory',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class SubcategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': '1',
            'message': 'Success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'status': '1',
                'message': 'Subcategory updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': '0',
            'message': 'Failed to update subcategory',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': '1',
            'message': 'Subcategory deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)