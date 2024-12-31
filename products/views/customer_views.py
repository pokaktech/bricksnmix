from django.utils import timezone
from django.db.models import Sum
from django.db.models.aggregates import Count, Avg
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.db.models import Q

from products.models import *
from products.serializers import *

from orders.models import OrderItem
from orders.models import Cart, CartItem

from accounts.models import Company
from accounts.serializers import CompanySerializer

from accounts.models import Company

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.generics import ListAPIView

from rest_framework import generics

from datetime import timedelta
from collections import defaultdict

from math import radians, cos, sin, sqrt, atan2
from django.http import JsonResponse
from geopy.geocoders import Nominatim
from django.db.models import F, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin



# Nearest Seller API
def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points using Haversine formula."""
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


class NearestSupplierView(APIView):
    def get(self, request):
        location = request.GET.get('location')  # e.g., "Kannur"
        lat = request.GET.get('latitude')
        lon = request.GET.get('longitude')
        radius = float(request.GET.get('radius', 10))  # Default to 10 km

        if location:
            # Convert location name to latitude and longitude
            geolocator = Nominatim(user_agent="myApp")
            geo_location = geolocator.geocode(location)
            if not geo_location:
                return Response({"Status": "0", "message": f"Location '{location}' not found."})
            lat, lon = geo_location.latitude, geo_location.longitude

        if not lat or not lon:
            return Response({"Status": "0", "message": "Please provide latitude and longitude or location."})

        # Find sellers within the radius
        sellers = Company.objects.annotate(
            distance_km=6371.0 * 2 * ACos(
                Cos(Radians(float(lat))) *
                Cos(Radians(F('latitude'))) *
                Cos(Radians(F('longitude')) - Radians(float(lon))) +
                Sin(Radians(float(lat))) * Sin(Radians(F('latitude')))
            , output_field=FloatField())  # Specify output_field explicitly
        ).filter(distance_km__lte=radius).order_by('distance_km')

        # seller_data = [{"name": s.name, "distance_km": round(s.distance_km, 2)} for s in sellers]
        # seller_data = [{"name": s.name, "logo": s.logo.url} for s in sellers]
        serializer = CompanySerializer(sellers, many=True)

        return JsonResponse({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })



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
        serializer = ProductSerializer(trending_products, many=True, context={'request': request})
        
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
        serializer = BrandSerializer(brands, many=True, context={'request': request})
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data}
        , status=status.HTTP_200_OK)        
    




# class OfferProductView(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request, format=None):
#         products = Product.objects.filter(offer_percent__gt=0, stock__gt=0)
#         serializer = ProductSerializer(products, many=True, context={'request': request})
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": serializer.data
#         })     





class CustomerBrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        brands = self.get_queryset()
        serializer = self.get_serializer(brands, many=True)

        return Response({
            'Status': '1',
            'message': 'Brand fetched successfully',
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
        })
    

class SpecificBrandListView(generics.ListAPIView):
    serializer_class = BrandSerializer

    def get_queryset(self):
        seller_id = self.kwargs.get('seller_id')
        return Brand.objects.filter(owner=seller_id)
    
    def list(self, request, *args, **kwargs):
        brands = self.get_queryset()
        serializer = self.get_serializer(brands, many=True)

        return Response({
            'Status': '1',
            'message': 'Brand fetched successfully',
            'Data': serializer.data
        })
    


class ProductSearchView(APIView):
    def post(self, request):
        search_word = request.data.get('search_word', '')
        if search_word:
            products = Product.objects.filter(name__icontains=search_word)
            serializer = ProductSerializer(products, many=True, context={'request': request})
            return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data})
        return Response({'Status': '0', 'message': 'Search word not provided'})
    


    



class BrandProductSearchView(APIView):
    def post(self, request, brand_id):
        search_word = request.data.get('search_word', '')
        if search_word:
            brand = get_object_or_404(Brand, id=brand_id)
            products = Product.objects.filter(brand=brand, name__icontains=search_word)
            serializer = ProductSerializer(products, many=True, context={'request': request})
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
        delivered_items = OrderItem.objects.filter(order__user=user, status='3', product=product)
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
            serializer = ProductSerializer(similar_product, many=True, context={'request': request})
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



class BannerListView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = CustomerBannerSerializer

    def get_queryset(self):
        return Banner.objects.filter(status='Approved')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = []

        for offer in queryset:
            # Serialize the offer
            offer_data = self.serializer_class(offer).data

            # Fetch products associated with the offer
            # offer_products = offer.offer_products.all()
            # enriched_offer_products = []

            # for offer_product in offer_products:
            #     # Serialize product details and merge with offer product details
            #     product_data = ProductSerializer(offer_product.product).data
            #     product_data.update({
            #         "discount_percentage": str(offer_product.discount_percentage),
            #         "product_offer_image": offer_product.product_offer_image.url if offer_product.product_offer_image else None,
            #     })
            #     enriched_offer_products.append(product_data)

            # # Add enriched products directly to the offer data
            # offer_data['offer_products'] = enriched_offer_products

            response_data.append(offer_data)

        return Response({
            'Status': '1',
            'message': 'Special offers retrieved successfully',
            'Data': response_data
        }, status=200)
    



class BannerProductsView(APIView):
    permission_classes = [AllowAny]  # Public API

    def get(self, request, banner_id):
        try:
            # Fetch the offer by ID
            banner = Banner.objects.get(id=banner_id, status='Approved')
        except Banner.DoesNotExist:
            return Response({
                'Status': '0',
                'message': 'Offer not found or not approved',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Fetch all products associated with the offer
        banner_products = BannerProduct.objects.filter(banner=banner)
        if not banner_products.exists():
            return Response({
                'Status': '0',
                'message': 'No products found for this offer',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the product data
        response_data = []
        for banner in banner_products:
            product_data = ProductSerializer(banner.product).data
            # product_data['discount_percentage'] = banner.discount_percentage
            product_data['product_banner_image'] = request.build_absolute_uri(banner.product_banner_image.url)
            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)
    


class SpecificBannerList(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = CustomerBannerSerializer

    def get_queryset(self):
        # Get seller_id from the URL parameters
        seller_id = self.kwargs.get('seller_id')
        return Banner.objects.filter(seller=seller_id, status='Approved')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = []

        for offer in queryset:
            offer_data = self.serializer_class(offer).data

            response_data.append(offer_data)

        return Response({
            'Status': '1',
            'message': 'Special offers retrieved successfully',
            'Data': response_data
        }, status=200)
    



# class SpecificBannerProducts(APIView):
#     permission_classes = [AllowAny]  # Public API

#     def get(self, request, banner_id, seller_id):
#         try:
#             # Fetch the offer by ID
#             banner = Banner.objects.get(id=banner_id, status='Approved')
#         except Banner.DoesNotExist:
#             return Response({
#                 'Status': '0',
#                 'message': 'Offer not found or not approved',
#                 'Data': []
#             }, status=status.HTTP_404_NOT_FOUND)

#         # Fetch all products associated with the offer
#         banner_products = BannerProduct.objects.filter(banner=banner)
#         if not banner_products.exists():
#             return Response({
#                 'Status': '0',
#                 'message': 'No products found for this offer',
#                 'Data': []
#             }, status=status.HTTP_404_NOT_FOUND)

#         # Serialize the product data
#         response_data = []
#         for banner in banner_products:
#             product_data = ProductSerializer(banner.product).data
#             # product_data['discount_percentage'] = banner.discount_percentage
#             product_data['product_banner_image'] = request.build_absolute_uri(banner.product_banner_image.url)
#             response_data.append(product_data)

#         return Response({
#             'Status': '1',
#             'message': 'Products retrieved successfully',
#             'Data': response_data
#         }, status=status.HTTP_200_OK)
    


class SpecialOfferProductsView(APIView):

    def get(self, request):
        # Get all special offer products
        special_offer_products = SpecialOfferProduct.objects.select_related('product', 'offer').all()

        # Group products by their offer
        offers_data = defaultdict(lambda: {"products": []})
        for sop in special_offer_products:
            offer_id = sop.offer.id
            offers_data[offer_id]["offer_title"] = sop.offer.title
            offers_data[offer_id]["banner"] = sop.offer.banner.url if sop.offer.banner else None

            # Serialize product data
            product_data = ProductSerializer(sop.product).data
            offers_data[offer_id]["products"].append(product_data)

        # Prepare response format
        response_data = [
            {
                "offer_title": data["offer_title"],
                "banner": data["banner"],
                "products": data["products"],
            }
            for data in offers_data.values()
        ]

        return Response({
            "Status": "1",
            "message": "Special offer products retrieved successfully",
            "data": response_data
        })



class SpecialOfferProductsSearchView(APIView):
    def post(self, request):
        # Get the search word from the request body
        search_word = request.data.get("search_word", "").strip()

        if not search_word:
            return Response({
                "Status": "0",
                "message": "Search word is required.",
                "data": []
            })

        # Filter special offer products based on the search word
        special_offer_products = SpecialOfferProduct.objects.select_related('product', 'offer').filter(
            Q(offer__title__icontains=search_word) |  # Search in offer title
            Q(product__name__icontains=search_word) |  # Search in product name
            Q(product__description__icontains=search_word)  # Search in product description
        )

        if not special_offer_products.exists():
            return Response({
                "Status": "0",
                "message": "No matching products or offers found.",
                "data": []
            })

        # Group products by their offer
        offers_data = defaultdict(lambda: {"products": []})
        for sop in special_offer_products:
            offer_id = sop.offer.id
            offers_data[offer_id]["offer_title"] = sop.offer.title
            offers_data[offer_id]["banner"] = sop.offer.banner.url if sop.offer.banner else None

            # Serialize product data
            product_data = ProductSerializer(sop.product).data
            offers_data[offer_id]["products"].append(product_data)

        # Prepare response format
        response_data = [
            {
                "offer_title": data["offer_title"],
                "banner": data["banner"],
                "products": data["products"],
            }
            for data in offers_data.values()
        ]

        return Response({
            "Status": "1",
            "message": "Search results retrieved successfully.",
            "data": response_data
        })
    



class SpecificSpecialOfferProducts(APIView):

    def get(self, request, seller_id):
        # Get all special offer products
        special_offer_products = SpecialOfferProduct.objects.select_related('product', 'offer').filter(product__vendor=seller_id)

        # Group products by their offer
        offers_data = defaultdict(lambda: {"products": []})
        for sop in special_offer_products:
            offer_id = sop.offer.id
            offers_data[offer_id]["offer_title"] = sop.offer.title
            offers_data[offer_id]["banner"] = sop.offer.banner.url if sop.offer.banner else None

            # Serialize product data
            product_data = ProductSerializer(sop.product).data
            offers_data[offer_id]["products"].append(product_data)

        # Prepare response format
        response_data = [
            {
                "offer_title": data["offer_title"],
                "banner": data["banner"],
                "products": data["products"],
            }
            for data in offers_data.values()
        ]

        return Response({
            "Status": "1",
            "message": "Special offer products retrieved successfully",
            "data": response_data
        })



class SellerAndProducts(APIView):
    def get(self, request, seller_id=None):
        # If a seller ID is passed, fetch that seller's products
        if seller_id:
            seller = get_object_or_404(User, id=seller_id, profile__user_type='seller')
            products = Product.objects.filter(vendor=seller)

            if products.exists():
                serializer = ProductSerializer(products, many=True)
                return Response({
                    'Status': '1',
                    'message': 'Success',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'Status': '0',
                    'message': 'No products found for this seller',
                    'data': []
                }, status=status.HTTP_200_OK)

        # If no seller ID is passed, fetch all sellers with names and images manually
        companies = Company.objects.filter(vendor__profile__user_type='seller')

        if companies.exists():
            # Prepare the response without using a serializer
            company_data = [
                {
                    'seller_id': company.vendor.id,
                    'name': company.name,
                    'logo': company.logo.url if company.logo else None
                }
                for company in companies
            ]

            return Response({
                'Status': '1',
                'message': 'All sellers retrieved successfully',
                'data': company_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'Status': '0',
                'message': 'No sellers found',
                'data': []
            }, status=status.HTTP_200_OK)

            

class TopRatedProductsView(APIView):
    def get(self, request):
        try:
            # Fetch products with an average rating of 4 or above
            high_rated_products = [
                product for product in Product.objects.all() 
                if product.get_average_rating() >= 4
            ]

            # Serialize the products
            serializer = ProductSerializer(high_rated_products, many=True)

            return Response({
                'Status': '1',
                'message': 'High-rated products retrieved successfully',
                'Data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'Status': '0',
                'message': f'Error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class CustomerSponsoredListView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = CustomerSponsoredSerializer

    def get_queryset(self):
        return Sponsored.objects.filter(status='Approved')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = []

        for sponsored in queryset:
            # Serialize the offer
            offer_data = self.serializer_class(sponsored).data
            response_data.append(offer_data)

        return Response({
            'Status': '1',
            'message': 'Sponsored retrieved successfully',
            'Data': response_data
        }, status=200)
    



class CustomerSponsoredProductsView(APIView):
    permission_classes = [AllowAny]  # Public API

    def get(self, request, sponsored_id):
        try:
            # Fetch the offer by ID
            sponsored = Sponsored.objects.get(id=sponsored_id, status='Approved')
        except Sponsored.DoesNotExist:
            return Response({
                'Status': '0',
                'message': 'Sponsored not found or not approved',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Fetch all products associated with the offer
        sponsored_products = SponsoredProduct.objects.filter(sponsored=sponsored)
        if not sponsored_products.exists():
            return Response({
                'Status': '0',
                'message': 'No products found for this sponsored',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the product data
        response_data = []
        for sponsored in sponsored_products:
            product_data = ProductSerializer(sponsored.product).data
            # product_data['discount_percentage'] = banner.discount_percentage
            # product_data['product_banner_image'] = request.build_absolute_uri(sponsored.product_banner_image.url)
            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)