from django.db.models import Sum
from django.utils import timezone


from products.models import Product, Banner, BannerProduct
from products.serializers import ProductSerializer, BannerSerializer

from datetime import timedelta, datetime


from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status






class ProductView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, product_id=None):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            if product_id is not None:
                product = Product.objects.get(id=product_id, vendor=user)
                serializer = ProductSerializer(product)
                return Response({'Status': '1', 'message': 'Success', 'Data': [serializer.data]}, status=status.HTTP_200_OK)
            else:
                # Fetch all products related to the vendor (seller)
                products = Product.objects.filter(vendor=user)
                serializer = ProductSerializer(products, many=True)
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        vendor = request.user  # Assuming the vendor is the logged-in user

        # Check if the user is a seller
        if vendor.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to add products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        # Create product data with the vendor set to the current user
        product_data = request.data.copy()  # Make a copy of request.data
        product_data['vendor'] = vendor.id  # Set vendor ID

        product_serializer = ProductSerializer(data=product_data, context={'request': request})
        if product_serializer.is_valid():
            product = product_serializer.save()
            # Return full product data after creation
            response_serializer = ProductSerializer(product)
            return Response({
            "Status": "1", 
            "message": "Product added successfully", 
            "Data": response_serializer.data
        }, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "0", "message": "Failed to add product", "Errors": product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id=None):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to update products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Fetch the product and ensure it belongs to the seller
            product = Product.objects.get(id=product_id, vendor=user)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)

        # Partial update: only update the fields provided in the request
        product_serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if product_serializer.is_valid():
            product_serializer.save()
            # Return full product data after update
            response_serializer = ProductSerializer(product)
            return Response({
            "Status": "1", 
            "message": "Product updated successfully", 
            "Data": response_serializer.data
        }, status=status.HTTP_200_OK)
        else:
            return Response({"Status": "0", "message": "Failed to update product", "Errors": product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, product_id=None):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to delete products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Fetch the product and ensure it belongs to the seller
            product = Product.objects.get(id=product_id, vendor=user)
            product.delete()
            return Response({"Status": "1", "message": "Product deleted successfully"}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)
        




class ProductStockView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, product_id=None):
        # Retrieve the product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a seller and if the product belongs to them
        if request.user.profile.user_type == 'seller' and product.vendor != request.user:
            return Response({'Status': '0', 'message': 'You are not authorized to view this product\'s stock'}, status=status.HTTP_403_FORBIDDEN)

        # Return the product stock
        return Response({
            'Status': '1',
            'product_id': product.id,
            'product_name': product.name,
            'stock': product.stock
        }, status=status.HTTP_200_OK)

    def put(self, request, product_id=None):
        # Check if the user is a seller
        if request.user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to update the stock'}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve the product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product belongs to the seller
        if product.vendor != request.user:
            return Response({'Status': '0', 'message': 'You are not authorized to update this product\'s stock'}, status=status.HTTP_403_FORBIDDEN)

        # Get the new stock value from the request data
        new_stock = request.data.get('stock')
        if new_stock is None:
            return Response({'Status': '0', 'message': 'Stock value is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the product stock
        product.stock = new_stock
        product.save()

        return Response({'Status': '1', 'message': 'Stock updated successfully', 'new_stock': product.stock}, status=status.HTTP_200_OK)
    

    




class SellerTotalProductView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            # Get total products
            total_products = Product.objects.filter(vendor=user).count()
            
            # Current month products
            current_month_start = datetime.now().replace(day=1)
            current_month_products = Product.objects.filter(
                vendor=user,
                created_at__gte=current_month_start
            ).count()
            
            # Previous month products
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            previous_month_products = Product.objects.filter(
                vendor=user,
                created_at__gte=previous_month_start,
                created_at__lte=previous_month_end
            ).count()
            
            # Calculate percentage change
            if previous_month_products > 0:
                change_percentage = ((current_month_products - previous_month_products) / previous_month_products) * 100
            else:
                change_percentage = 100 if current_month_products > 0 else 0
                
            data = [{
                'total_products': total_products,
                'change_percentage': round(change_percentage, 2)
            }]
            
            return Response({
                'Status': '1',
                'message': 'Success',
                'data': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'Status': '1',
                'message': "You are not a seller"
            })
        



class SellerTopSellingProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.profile.user_type == "seller":
            # Define a time range, e.g., past 30 days
            days_range = 30
            time_threshold = timezone.now() - timedelta(days=days_range)

            # Annotate products with the sum of quantities sold in the given time range
            top_selling_products = Product.objects.filter(
                vendor=user,
                orderitem__order__created_at__gte=time_threshold, stock__gt=0
            ).annotate(
                total_sales=Sum('orderitem__quantity')
            ).order_by('-total_sales')[:5]  # Top 5 top selling products

            # Serialize the products (assuming you have a ProductSerializer)
            serializer = ProductSerializer(top_selling_products, many=True, context={'request': request})
            return Response({"Status": "1", "message": "Success", "Data": serializer.data})
        else:
            return Response({"Status": "1", "message": "You are not a seller"})
        

            

class AddBannerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BannerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"Status": "1", "message": "Banner created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"Status": "0", "message": "Error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)