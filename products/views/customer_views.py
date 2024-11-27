from django.utils import timezone
from django.db.models import Sum
from django.db.models.aggregates import Count
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from products.models import RatingReview
from products.serializers import RatingReviewSerializer, BrandSerializer, ProductSerializer
from products.models import Brand, Product, Productimg, Wishlist, WishlistItem

from orders.models import OrderItem
from orders.models import Cart, CartItem

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from rest_framework import generics

from datetime import timedelta







class TrendingProductAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Define the time range for "trending" (e.g., last 30 days)
        last_30_days = now() - timedelta(days=30)
        
        # Annotate products with the count of how many times they appear in orders within the last 30 days
        trending_products = Product.objects.filter(
            orderitem__order__created_at__gte=last_30_days, stock__gt=0
        ).annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:10]  # Get top 10 trending products
        
        # Serialize the trending products
        serializer = ProductSerializer(trending_products, many=True)
        
        return Response({"Status": "1", "message": "Success", "Data": serializer.data}, status=status.HTTP_200_OK)



class FastMovingProductsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Define a time range, e.g., past 30 days
        days_range = 30
        time_threshold = timezone.now() - timedelta(days=days_range)

        # Annotate products with the sum of quantities sold in the given time range
        fast_moving_products = Product.objects.filter(
            orderitem__order__created_at__gte=time_threshold, stock__gt=0
        ).annotate(
            total_sales=Sum('orderitem__quantity')
        ).order_by('-total_sales')[:10]  # Top 10 fast-moving products

        # Serialize the products (assuming you have a ProductSerializer)
        serializer = ProductSerializer(fast_moving_products, many=True, context={'request': request})
        return Response({"Status": "1", "message": "Success", "Data": serializer.data})
    


class ProductDetail(APIView):
    def get(self, request, product_id=None):
        try:
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                serializer = ProductSerializer(product, context={'request': request})
                return Response({'Status': '1', 'message': 'Success', 'Data': [serializer.data]}, status=status.HTTP_200_OK)
            else:
                products = Product.objects.filter(stock__gt=0)
                serializer = ProductSerializer(products, many=True, context={'request': request})
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    

        


class TrendingBrandsView(APIView):
    def get(self, request, format=None):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data}
        , status=status.HTTP_200_OK)        
    




class OfferProductView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        products = Product.objects.filter(offer_percent__gt=0, stock__gt=0)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })     





class CustomerBrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)

        return Response({
            'Status': '1',
            'message': 'Categories fetched successfully',
            'Data': serializer.data
        })
    



class CustomerBrandDetailView(APIView):
    def get(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return Response({
                'Status': '0',
                'message': 'Brand not found',
                'Data': None
            }, status=404)

        # Get products associated with the category
        products = Product.objects.filter(brand=brand)
        product_serializer = ProductSerializer(products, many=True)

        # Return category and products
        return Response({
            'Status': '1',
            'message': 'Brand details fetched successfully',
            'Data': product_serializer.data
                # 'category': CustomerCategorySerializer(category).data,
            
        })
    


class ProductSearchView(APIView):
    def post(self, request):
        search_word = request.data.get('search_word', '')
        if search_word:
            products = Product.objects.filter(name__icontains=search_word)
            serializer = ProductSerializer(products, many=True)
            return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data})
        return Response({'Status': '0', 'message': 'Search word not provided'})
    


    



class BrandProductSearchView(APIView):
    def post(self, request, brand_id):
        search_word = request.data.get('search_word', '')
        if search_word:
            brand = get_object_or_404(Brand, id=brand_id)
            products = Product.objects.filter(brand=brand, name__icontains=search_word)
            serializer = ProductSerializer(products, many=True)
            return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data})
        return Response({'Status': '0', 'message': 'Search word not provided'})
    





class ProductMinimumQuantityView(APIView):
    def get(self, request, product_id):
        try:
            try:
                product = Product.objects.get(id=product_id)
            except:
                return Response({
                    'Status': '0',
                    'message': 'No product found'
                })
            data = [{
                "min_order_quantity": product.min_order_quantity,
                "min_order_quantity_two": product.min_order_quantity_two,
                "min_order_quantity_three": product.min_order_quantity_three,
                "min_order_quantity_four": product.min_order_quantity_four,
                "min_order_quantity_five": product.min_order_quantity_five
            }]
            return Response({
                "Status": '1',
                "message": 'Success',
                "data": data
            })
        except:
            return Response({
                "Status": '0',
                "message": 'You have to provide product id'
            })
        



class WishlistView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None


        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session['initialized'] = True
                request.session.save()
            session_id = request.session.session_key
        wishlist, created = Wishlist.objects.get_or_create(user=user) if user else Wishlist.objects.get_or_create(session_id=session_id)

        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)

        # Prepare the cart items data
        items = []
        for item in wishlist_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None  # Choose the first image or None if no image
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'description': item.product.description,
                'product_images': f"/media/{product_image}" if product_image != None else None,
                'price_per_item': item.product.price,
                'delivery_charge': item.product.delivery_charge,
                'offer_percent': item.product.offer_percent,
                'min_order_quantity': item.product.min_order_quantity,
                'min_order_quantity_two': item.product.min_order_quantity_two,
                'min_order_quantity_three': item.product.min_order_quantity_three,
                'min_order_quantity_four': item.product.min_order_quantity_four,
                'min_order_quantity_five': item.product.min_order_quantity_five,
                'created_at': item.added_at
            })

        return Response({
            'Status': '1',
            'wishlist_id': wishlist.id,
            'total_items': len(items),
            'items': items,
        }, status=status.HTTP_200_OK)

    

    def post(self, request):
        product_id = request.data.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        user = request.user if request.user.is_authenticated else None

        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session['initialized'] = True
                request.session.save()
            session_id = request.session.session_key
        
        if not product:
            return Response({
                'Status': '0',
                'Message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's wishlist

        # session_id = request.session.session_key  # Get the session key
        wishlist, created = Wishlist.objects.get_or_create(user=user) if user else Wishlist.objects.get_or_create(session_id=session_id)

        # Add the product to the wishlist
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

        return Response({
            'Status': '1',
            'Message': 'Product added to wishlist'
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        # Get the user's wishlist
        # wishlist = Wishlist.objects.filter(user=request.user).first()
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            session_id = request.session.session_key
        wishlist = Wishlist.objects.filter(user=user).first() if user else Wishlist.objects.filter(session_id=session_id).first()
        if wishlist:
            wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).first()
            if wishlist_item:
                wishlist_item.delete()
                return Response({
                    'Status': '1',
                    'message': 'Product removed from wishlist'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'Status': '0',
                    'message': 'Product not in wishlist'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'Status': '0',
            'message': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    



class WishListFromCartView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        product_id = request.data.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        user = request.user if request.user.is_authenticated else None

        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session['initialized'] = True
                request.session.save()
            session_id = request.session.session_key
        
        if not product:
            return Response({
                'Status': '0',
                'Message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        
        wishlist, created = Wishlist.objects.get_or_create(user=user) if user else Wishlist.objects.get_or_create(session_id=session_id)

        # Add the product to the wishlist
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        try:
            cart = Cart.objects.get(user=user) if user else Cart.objects.get(session_id=session_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
        except:
            pass

        return Response({
            'Status': '1',
            'Message': 'Product moved to wishlist succesfully'
        }, status=status.HTTP_201_CREATED)
    



class ProductReviewList(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def get(self, request, product_id):
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all reviews for the specified product
        reviews = RatingReview.objects.filter(product_id=product_id)
        serializer = RatingReviewSerializer(reviews, many=True)
        return Response({
            "Status": '1',
            "message": "Success",
            "Data": serializer.data
        }, status=status.HTTP_200_OK)
        # return Response(serializer.data, status=status.HTTP_200_OK)



class AddProductReview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Check if the user is a customer
        if not user.profile.user_type:  # Assuming you have a field to identify customer users
            return Response({"error": "Only customers can add reviews."}, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('product_id')
        rating = request.data.get('rating')
        comments = request.data.get('comments')

        if not product_id or not rating:
            return Response({"error": "Product ID and rating are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product was in the user's delivered orders
        delivered_items = OrderItem.objects.filter(order__user=user, status='2', product=product)
        deli = OrderItem.objects.filter(order__user=user, product=product)
        print(deli.exists())
        if not delivered_items.exists():
            return Response({"error": "You cannot review this product because you have not purchased it."}, status=status.HTTP_403_FORBIDDEN)

        # Save the review
        data = {
            'product': product_id,
            'user': user.id,
            'rating': rating,
            'comments': comments
        }
        serializer = RatingReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class SimilarProductsView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            similar_product = Product.objects.filter(category=product.category).exclude(id=product.id)
            serializer = ProductSerializer(similar_product, many=True)
            return Response({
                'Status': 'Ok',
                'message': 'Success',
                'data': serializer.data
            })
        except:
            return Response({
                'Status': 'Ok',
                'message': 'Product not Found'
            })