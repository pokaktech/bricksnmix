from django.shortcuts import render, redirect
from .forms import UserCreationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from orders.models import Order, OrderDetails
from django.views.generic import View, TemplateView
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404 
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Profile, TemporaryUserContact
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.conf import settings
from wsgiref.util import FileWrapper
# Import mimetypes module
import mimetypes
# import os module
import os
# Import HttpResponse module
from django.http.response import HttpResponse
from django.utils import timezone


# Create your views here.
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Category, Subcategory, RatingReview
from .serializers import CategorySerializer,RatingReviewSerializer, DeliveryAddressSerializer
from rest_framework import status
from .models import Banner, Brand, Product, Productimg, Cart, CartItem, OrderProductImage, SuperAdmin
from .serializers import BannerSerializer, BrandSerializer, OfferProductSerializer, ProductSerializer, ProductimgSerializer,CartSerializer, CartItemSerializer, CustomerSignupSerializer, SellerSignupSerializer, WishlistSerializer
from django.shortcuts import get_object_or_404
from .models import CustomerOrder, OrderItem
from .serializers import CustomerOrderSerializer, OrderItemSerializer, CustomerCategorySerializer
from accounts.models import DeliveryAddress
from .models import Wishlist, WishlistItem
from .models import BankAccount
from .serializers import BankAccountSerializer
from rest_framework import generics
from .models import BankAccount
from .serializers import BankAccountSerializer, ProfileSerializer, SubcategorySerializer
from .models import SocialLink
from django.utils.crypto import get_random_string

from .serializers import SocialLinkSerializer

from django.db.models.aggregates import Count
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum


from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get('email')
            name = data.get('Name')
            phone = data.get('Phone')
            user_type = data.get('Type')
            gst = data.get('Gst')
            shopname = data.get('Shopname')
            logoimage = data.get('Logoimage')
            company_name = data.get('Company name')
            latitude = data.get('Latitude')
            longitude = data.get('longitude')
            password = data.get('Password')

            if not email or not password:
                return Response({'Status': '0', 'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({'Status': '0', 'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create user
            new_user = User.objects.create_user(username=email, email=email, password=password)
            new_user.first_name = name
            new_user.save()

            # Create or update profile
            profile, created = Profile.objects.get_or_create(user=new_user)
            profile.email = email
            profile.name = name
            profile.phone = phone
            profile.type = user_type
            profile.gst = gst
            profile.shopname = shopname
            profile.company_name = company_name
            profile.latitude = latitude
            profile.longitude = longitude
            profile.status = 'vendor' if user_type.lower() == 'seller' else 'customer'
            profile.save()

            # Handle logoimage (you might want to use a file upload handler here)
            # For now, we're just storing the string, which isn't ideal for images
            if logoimage:
                profile.logoimage = logoimage
                profile.save()

            return Response({
                'Status': '1',
                'message': 'Success',
                'Data': {
                    'name': profile.name,
                    'Mobile': profile.phone,
                    'userid': new_user.id,
                    'Type': profile.type
                }
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError:
            return Response({'Status': '0', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Status': '0', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('Password')

            if not email or not password:
                return Response({'Status': '0', 'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                return Response({'Status': '0', 'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

            if user is not None:
                login(request, user)
                profile = Profile.objects.get(user=user)
                return Response({
                    'Status': '1',
                    'message': 'Success',
                    'Data': {
                        'name': profile.name,
                        'Mobile': profile.phone,
                        'userid': user.id,
                        'Type': profile.type
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'Status': '0', 'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        except json.JSONDecodeError:
            return Response({'Status': '0', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Status': '0', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def logout_user(request):
    logout(request)
    messages.success(
        request, 'Your Now Logout !')
    return redirect('accounts:login')


def dashboard_customer(request):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')
    context = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        display_name = request.POST['display_name']
        bio = request.POST['bio']
        mobile_number = request.POST['mobile_number']
        city = request.POST['city']
        address = request.POST['address']
        post_code = request.POST['post_code']
        country = request.POST['country']
        state = request.POST['state']
        user = User.objects.get(username=request.user)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        profile = Profile.objects.get(user=request.user)
        try:
            image = request.FILES["image"]

        except:
            image = None

        if image:
            profile.image = image
        profile.display_name = display_name
        profile.bio = bio
        profile.mobile_number = mobile_number
        profile.city = city
        profile.address = address
        profile.post_code = post_code
        profile.country = country
        profile.state = state
        profile.save()
        messages.success(
            request, 'Your Profile Info Has Been Saved !')
        return redirect("accounts:dashboard_customer")

    else:
        profile = Profile.objects.get(
            user=request.user)
        print(profile)
        context = {
            "profile": profile,
        }
    return render(request, 'accounts/page-account.html', context)



def dashboard_account_details(request):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')
    context = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        display_name = request.POST['display_name']
        bio = request.POST['bio']
        mobile_number = request.POST['mobile_number']
        city = request.POST['city']
        address = request.POST['address']
        post_code = request.POST['post_code']
        country = request.POST['country']
        state = request.POST['state']
        user = User.objects.get(username=request.user)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        profile = Profile.objects.get(user=request.user)
        try:
            image = request.FILES["image"]

        except:
            image = None

        if image:
            profile.image = image

        if image:
            try:
                Image.open(image)

            except:
                messages.warning(request, 'sorry, your image is invalid')
                return redirect("accounts:account_details")
        profile.display_name = display_name
        profile.bio = bio
        profile.mobile_number = mobile_number
        profile.city = city
        profile.address = address
        profile.post_code = post_code
        profile.country = country
        profile.state = state
        profile.save()
        messages.success(
            request, 'Your Profile Info Has Been Saved !')
        return redirect("accounts:account_details")

    else:
        profile = Profile.objects.get(
            user=request.user)
        print(profile)
        context = {
            "profile": profile,
        }
    return render(request, 'accounts/account-details.html', context)


def order_tracking(request):

    return render(request, 'accounts/order-tracking.html')


@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            login(request, request.user)
            messages.success(
                request, 'Password successfully changed!')
            return redirect('accounts:change_password')

        else:
            messages.warning(request, 'Please fix the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change-password.html",  {
        'form': form,

        'title': 'Change Password',
    }

    )


class MyOrdersJsonListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        upper = int(self.request.GET.get("num_products"))
        lower = upper - 10
        orders = list(Order.objects.all().filter(
            user=self.request.user).values().order_by("-order_date")[lower:upper])
        orders_size = len(Order.objects.all().filter(user=self.request.user))
        max_size = True if upper >= orders_size else False
        return JsonResponse({"data": orders,  "max": max_size, "orders_size": orders_size, }, safe=False)


def order(request, order_id):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')
    context = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.all().filter(id=order_id, user=request.user, is_finished=True):
            order = Order.objects.get(id=order_id, user=request.user)
            order_details = OrderDetails.objects.all().filter(order=order)
            total = 0
            for sub in order_details:
                total += sub.price * sub.quantity
            context = {
                "order": order,
                "order_details": order_details,
                "total": total,
            }
        elif Order.objects.all().filter(id=order_id, user=request.user, is_finished=False):
            return redirect('orders:cart')
        else:
            messages.warning(
                request, "You don't have access to this page !")
            return redirect('accounts:dashboard_customer')
    return render(request, "accounts/order-archive.html", context)


@login_required(login_url='accounts:login')
def download_list(request):
    order_list = Order.objects.all().filter(
        user=request.user, is_finished=True).order_by("-order_date")
    files = {}
    for order in order_list:
        print(order.id)
        order_details = OrderDetails.objects.all().filter(order=order)
        for file in order_details:
            if file.product.digital_file:
                files[int(order.id)] = str(
                    file.product.digital_file.name.split('/')[-1])
        print(files)
    context = {
        "files": files,
    }
    return render(request, 'accounts/download-page.html', context)


@login_required(login_url='accounts:login')
def download_file(request, order_id, filename):
    if request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.all().filter(id=order_id, user=request.user, is_finished=True):
            # Define Django project base directory
            # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            BASE_DIR = settings.MEDIA_ROOT
            # Define the full file path
            filepath = BASE_DIR + '/products/files/' + filename
            # filepath = os.path.join(settings.MEDIA_ROOT, filename)
            print(filepath)
            # Open the file for reading content
            # path = open(filepath, 'rb')
            path = FileWrapper(open(filepath, 'rb'))
            # Set the mime type
            mime_type, _ = mimetypes.guess_type(filepath)
            # Set the return value of the HttpResponse
            response = HttpResponse(path, content_type=mime_type)
            # Set the HTTP header for sending to browser
            response['Content-Disposition'] = f"attachment; filename={filename}"
            # Return the response value
            return response

        elif Order.objects.all().filter(id=order_id, user=request.user, is_finished=False):
            return redirect('orders:cart')
        else:
            messages.warning(
                request, "You don't have access to this page !")
            return redirect('accounts:dashboard_customer')

# class CategoryListView(APIView):
#     def get(self, request, format=None):
#         categories = Category.objects.all()
#         serializer = CategorySerializer(categories, many=True)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": serializer.data
#         })
        
#     def post(self, request, format=None):
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             category = Category.objects.create(
#                 name=serializer.validated_data['categoryname'],
#                 image=serializer.validated_data.get('image', '')
#             )
#             for subcategory_data in serializer.validated_data['subcategories']:
#                 Subcategory.objects.create(
#                     category=category,
#                     name=subcategory_data['subcategoryname'],
#                     image=subcategory_data.get('image', '')
#                 )
#             return Response({
#                 "Status": "1",
#                 "message": "Category created successfully",
#                 "Data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "Status": "0",
#             "message": "Error",
#             "Data": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

class BannerListView(APIView):
    def get(self, request, format=None):
        print("check")
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })        
        
    def post(self, request, format=None):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Banner added successfully",
                "Data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Status": "0",
            "message": "Error",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)    
        
class AddBrandView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, format=None):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Brand added successfully",
                "Data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Status": "0",
            "message": "Failed to add brand",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    # parser_classes = (MultiPartParser, FormParser)
    # def post(self, request, format=None):
    #         brand_id = request.data.get('id')
    #         if not brand_id:
    #             return Response({
    #                 "Status": "0",
    #                 "message": "Failed to add brand",
    #                 "Errors": {"id": ["This field is required."]}
    #             }, status=status.HTTP_400_BAD_REQUEST)
            
    #         try:
    #             brand = Brand.objects.get(id=brand_id)
    #             serializer = BrandSerializer(brand, data=request.data)
    #         except Brand.DoesNotExist:
    #             serializer = BrandSerializer(data=request.data)
            
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({
    #                 "Status": "1",
    #                 "message": "Brand added successfully",
    #                 "Data": serializer.data
    #             }, status=status.HTTP_201_CREATED)
            
    #         return Response({
    #             "Status": "0",
    #             "message": "Failed to add brand",
    #             "Errors": serializer.errors
    #         }, status=status.HTTP_400_BAD_REQUEST)            
                
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
        serializer = ProductSerializer(products, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })     
        

# class ProductDetailView(APIView):
#     def post(self, request, format=None):
#         product_id = request.data.get('product_id')
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({
#                 "Status": "0",
#                 "message": "Product not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         serializer = ProductDetailSerializer(product)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": [serializer.data]
#         })        
class ProductDetail(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]
    def get(self, request, product_id=None):
        try:
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                serializer = ProductSerializer(product)
                return Response({'Status': '1', 'message': 'Success', 'Data': [serializer.data]}, status=status.HTTP_200_OK)
            else:
                products = Product.objects.filter(stock__gt=0)
                serializer = ProductSerializer(products, many=True)
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # def post(self, request):
    # # Extract vendor from the request
    #     vendor = request.user  # Assuming the vendor is the logged-in user

    #     # Create product data with the vendor set to the current user
    #     product_data = request.data.copy()  # Make a copy of request.data
    #     product_data['vendor'] = vendor.id  # Set vendor ID

    #     product_serializer = ProductSerializer(data=product_data, context={'request': request})
    #     if product_serializer.is_valid():
    #         product = product_serializer.save()
    #         images_data = request.FILES.getlist('images')
    #         for image_data in images_data:
    #             Productimg.objects.create(product=product, image=image_data)
    #         return Response({"Status": "1", "message": "Product added successfully"}, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response({"Status": "0", "message": "Failed to add product", "Errors": product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        

# @method_decorator(csrf_exempt, name='dispatch')
# class CategoryCreateView(APIView):
#     def post(self, request, format=None):
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "Status": "1",
#                 "message": "Category added successfully",
#                 "Data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "Status": "0",
#             "message": "Failed to add category",
#             "Errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class CategoryListView(APIView):
#     def get(self, request, format=None):
#         categories = Category.objects.all()
#         serializer = CategorySerializer(categories, many=True)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": serializer.data
#         }, status=status.HTTP_200_OK)     


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

        
        
# class ProductSearchView(APIView):
    
#     def post(self, request):
#         search_word = request.data.get('search_word', '')
#         category = request.data.get('category', '')
#         brand = request.data.get('brand', '')
#         # subcategory = request.get('subcategory', '')
#         # trending_products = request.get('trending_products', '')
#         if search_word:
#             if category:
#                 category_obj = Category.objects.get(id=category)
#                 products = Product.objects.filter(category=category_obj)
#             if brand:
#                 # brand_obj = Brand.objects.get(id=brand)
#                 brand_obj = get_object_or_404(Brand, id=brand)
#                 if brand_obj:
#                     products = Product.objects.filter(brand=brand_obj)
#                     serializer = ProductSerializer(products, many=True)
#                     return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
#                 else:
#                     return Response({'Status': '0', 'message': 'Brand not found'}, status=status.HTTP_400_BAD_REQUEST)
#             products = Product.objects.filter(name__icontains=search_word)
#             serializer = ProductSerializer(products, many=True)
#             return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
#         else:
#             return Response({'Status': '0', 'message': 'Search word not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
class RatingReviewListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reviews = RatingReview.objects.all()
        serializer = RatingReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RatingReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RatingReviewDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return RatingReview.objects.get(pk=pk)
        except RatingReview.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        review = self.get_object(pk)
        serializer = RatingReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        review = self.get_object(pk)
        serializer = RatingReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        review = self.get_object(pk)
        serializer = RatingReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# class GetRatingAndReviews(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         reviews = RatingReview.objects.all()
#         serializer = RatingReviewSerializer(reviews, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = RatingReviewSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class AddRatingAndReviews(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         product_id = request.data.get('productid')
#         rating = request.data.get('rating')
#         user_id = request.data.get('Userid')
#         comments = request.data.get('comments', '')

#         if not product_id or not rating or not user_id:
#             return Response({'Status': '0', 'message': 'Product ID, rating, and user ID are required'}, status=status.HTTP_400_BAD_REQUEST)

#         user = User.objects.get(id=user_id)
#         review = RatingReview.objects.create(product_id=product_id, rating=rating, user=user, comments=comments)
#         review.save()

#         return Response({'Status': '1', 'message': 'Success'}, status=status.HTTP_201_CREATED)        
    
# class UpdateRatingAndReviews(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         rating_id = request.data.get("ratingid")
#         product_id = request.data.get("productid")
#         rating = request.data.get("rating")
#         user_id = request.data.get("Userid")
#         comments = request.data.get("comments")

#         if not rating_id or not product_id or not rating or not user_id:
#             return JsonResponse({"Status": "0", "message": "Rating ID, Product ID, rating, and User ID are required"}, status=400)

#         try:
#             review = RatingReview.objects.get(id=rating_id)
#             product = Product.objects.get(id=product_id)
#             user = User.objects.get(id=user_id)
#         except RatingReview.DoesNotExist:
#             return JsonResponse({"Status": "0", "message": "Rating and Review not found"}, status=404)
#         except Product.DoesNotExist:
#             return JsonResponse({"Status": "0", "message": "Product not found"}, status=404)
#         except User.DoesNotExist:
#             return JsonResponse({"Status": "0", "message": "User not found"}, status=404)

#         review.product = product
#         review.user = user
#         review.rating = rating
#         review.comments = comments
#         review.save()
        
#         return JsonResponse({"Status": "1", "message": "Success"}, status=200)


# class DeleteRatingAndReviews(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         rating_id = request.data.get("ratingid")
#         product_id = request.data.get("productid")

#         if not rating_id or not product_id:
#             return JsonResponse({"Status": "0", "message": "Rating ID and Product ID are required"}, status=400)

#         try:
#             review = RatingReview.objects.get(id=rating_id, product_id=product_id)
#         except RatingReview.DoesNotExist:
#             return JsonResponse({"Status": "0", "message": "Rating and Review not found"}, status=404)

#         review.delete()
#         return JsonResponse({"Status": "1", "message": "Success"}, status=200)    
    
# class CartView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]

#     def get(self, request):
#         user = request.user

#         try:
#             cart = Cart.objects.get(user=user)
#         except Cart.DoesNotExist:
#             return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

#         cart_items = CartItem.objects.filter(cart=cart)

#         # Prepare the cart items data
#         items = []
#         for item in cart_items:
#             items.append({
#                 'product_id': item.product.id,
#                 'product_name': item.product.name,
#                 'quantity': item.quantity,
#                 'price_per_item': item.product.price,
#                 'total_price': item.quantity * item.product.price
#             })

#         return Response({
#             'Status': '1',
#             'cart_id': cart.id,
#             'total_items': len(items),
#             'items': items,
#         }, status=status.HTTP_200_OK)  
    

#     def post(self, request):
#         product_id = request.data.get('product_id')
#         quantity = request.data.get('quantity')

#         # Debugging print statements
#         print(f"Request data: Product ID = {product_id}, Quantity = {quantity}")

#         if not product_id or not quantity:
#             return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

#         user = request.user

#         # Debugging print statement
#         print(f"User ID: {user.id}")

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

#         # Debugging print statement
#         print(f"Product ID: {product.id}, Stock: {product.stock}")

#         if product.stock < int(quantity):
#             return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

#         cart, created = Cart.objects.get_or_create(user=user)
#         # Debugging print statement
#         print(f"Cart ID: {cart.id}, Created: {created}")

#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         # Debugging print statement
#         print(f"Cart Item: {cart_item}, Created: {created}")

#         if created:
#             cart_item.quantity = int(quantity)
#         else:
#             if cart_item.quantity + int(quantity) > product.stock:
#                 return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
#             cart_item.quantity += int(quantity)

#         cart_item.save()

#         # Update the product stock
#         product.stock -= int(quantity)
#         if product.stock < 0:
#             return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
#         product.save()

#         return Response({"Status": "1", "message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)
    
# class GetCart(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]

#     def get(self, request):
#         user = request.user

#         try:
#             cart = Cart.objects.get(user=user)
#         except Cart.DoesNotExist:
#             return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

#         cart_items = CartItem.objects.filter(cart=cart)

#         # Prepare the cart items data
#         items = []
#         for item in cart_items:
#             items.append({
#                 'product_id': item.product.id,
#                 'product_name': item.product.name,
#                 'quantity': item.quantity,
#                 'price_per_item': item.product.price,
#                 'total_price': item.quantity * item.product.price
#             })

#         return Response({
#             'Status': '1',
#             'cart_id': cart.id,
#             'total_items': len(items),
#             'items': items,
#         }, status=status.HTTP_200_OK)        

# class UpdateCart(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     def post(self, request):
#         cart_item_id = request.data.get('Cartid')
#         quantity = request.data.get('quantity')

#         if not cart_item_id or not quantity:
#             return Response({'Status': '0', 'message': 'Cart ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             cart_item = CartItem.objects.get(id=cart_item_id)
#         except CartItem.DoesNotExist:
#             return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

#         if cart_item.product.stock + cart_item.quantity < int(quantity):
#             return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

#         cart_item.product.stock += cart_item.quantity - int(quantity)
#         cart_item.product.save()
#         cart_item.quantity = int(quantity)
#         cart_item.save()

#         return Response({"Status": "1", "message": "Cart updated successfully"}, status=status.HTTP_200_OK)  

class PlaceOrderView(APIView):
    def post(self, request):
        serializer = CustomerOrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            # Handle OrderItem creation here
            for item_data in request.data.get('Data', []):
                item_data['order'] = order.id
                item_serializer = OrderItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    item_serializer.save()
            return Response({"Status": "1", "message": "Success"}, status=status.HTTP_201_CREATED)
        return Response({"Status": "0", "message": "Failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class GetOrdersView(APIView):
    def post(self, request):
        user_id = request.data.get('userid')
        orders = CustomerOrder.objects.filter(user_id=user_id)
        if orders.exists():
            order = orders.first()  # Assuming you want to return the first order
            serializer = CustomerOrderSerializer(order)
            return Response({"Status": "1", "message": "Success", "data": serializer.data})
        return Response({"Status": "0", "message": "No orders found"}, status=status.HTTP_404_NOT_FOUND)

class GetDeliveryChargeView(APIView):
    def get(self, request):
        # You can set a fixed delivery charge or calculate it based on some logic
        delivery_charge = 10.22  # Example value
        return Response({"Status": "1", "message": "Success", "Deliverycharge": delivery_charge})

class DeleteFromCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_item_id = request.data.get('Cartid')

        if not cart_item_id:
            return Response({'Status': '0', 'message': 'Cart ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Restore the product stock before deleting the item
        cart_item.product.stock += cart_item.quantity
        cart_item.product.save()

        cart_item.delete()

        return Response({"Status": "1", "message": "Item removed from cart successfully"}, status=status.HTTP_200_OK)

class AddToWishlist(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('productid')

        if not product_id:
            return Response({'Status': '0', 'message': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        wishlist, created = Wishlist.objects.get_or_create(user=user)
        wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

        if created:
            return Response({'Status': '1', 'message': 'Success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'Status': '0', 'message': 'Product already in wishlist'}, status=status.HTTP_200_OK)

class DeleteFromWishlist(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wishlist_item_id = request.data.get('wishlistid')

        if not wishlist_item_id:
            return Response({'Status': '0', 'message': 'Wishlist ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
        except WishlistItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Wishlist item not found'}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item.delete()

        return Response({"Status": "1", "message": "Success"}, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            name = request.data.get('name')
            phone = request.data.get('phone')
            user_type = request.data.get('type')
            gst = request.data.get('gst')
            shopname = request.data.get('shopname')
            logoimage = request.data.get('logoimage')
            company_name = request.data.get('company_name')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            password = request.data.get('password')

            if not user_id:
                return Response({'Status': '0', 'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'Status': '0', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            profile, created = Profile.objects.get_or_create(user=user)

            if name:
                profile.name = name
            if phone:
                profile.phone = phone
            if user_type:
                profile.type = user_type
                profile.status = 'vendor' if user_type.lower() == 'seller' else 'customer'
            if gst:
                profile.gst = gst
            if shopname:
                profile.shopname = shopname
            if company_name:
                profile.company_name = company_name
            if latitude:
                profile.latitude = latitude
            if longitude:
                profile.longitude = longitude
            if logoimage:
                profile.logoimage = logoimage
            if password:
                user.set_password(password)
                user.save()

            profile.save()

            return Response({
                'Status': '1',
                'message': 'Success'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'Status': '0', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)  

class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
#below code added ---------------------
    def perform_create(self, serializer):
        user = self.request.user
        if user and not Profile.objects.filter(user=user).exists():
            serializer.save(user=user)
        else:
            serializer.save()

class ProfileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer  
class BankAccountListCreateView(generics.ListCreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

class BankAccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
class SocialLinkListCreateView(generics.ListCreateAPIView):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer

class SocialLinkRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer



class GetOrderBySellerID(APIView):
    def post(self, request):
        seller_id = request.data.get('sellerid')
        if not seller_id:
            return Response({"Status": "0", "message": "Seller ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        seller = get_object_or_404(User, id=seller_id)
        orders = CustomerOrder.objects.filter(user=seller)
        print(orders)
        order_data = []
        for order in orders:
            delivery_address = order.delivery_address
            address_serializer = DeliveryAddressSerializer(delivery_address)

            # Fetch related order items
            order_items = OrderItem.objects.filter(order=order)
            items_data = []
            
            for item in order_items:
                # Adding detailed product and category information
                item_data = {
                    "id": item.id,
                    "Categoryid": item.product.category.id if item.product.category else None,
                    "Productid": item.product.id,
                    "name": item.product.name,
                    "Price": str(item.product.price),
                    "Offerpercent": str(item.product.offer_percent),
                    "Actualprice": str(item.product.actual_price),
                    "Quantity": item.quantity,
                    "Image": [{"image": img.image.url} for img in OrderProductImage.objects.filter(order_item=item)],
                    "Description": item.product.description or ""
                }
                items_data.append(item_data)
            
            # Create a dictionary with all the needed order information
            order_dict = {
                "id": order.id,
                "Total_price": str(order.total_price),
                "Deliverycharge": str(order.delivery_charge),
                "NetTotal": str(order.net_total),
                "Delivery_status": order.status,
                "payment_type": order.payment_type,
                "Delivery_address": address_serializer.data,
                "Data": items_data  # Attach the detailed items data here
            }
            
            order_data.append(order_dict)

        return Response({"Status": "1", "message": "Success", "Data": order_data}, status=status.HTTP_200_OK)
    

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
    



class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        # serializer.is_valid(raise_exception=True)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({
                "status": "0",
                "message": "Invalid username or password"
            }, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = token.user.profile.user_type
        print(user_type)
        data = {"access": token.key, "user_type": user_type, "user_name": user.username, "email": user.email}
        if user_type == "customer":
            self.merge_cart(user)
            self.merge_wishlist(user)
            try:
                cart = Cart.objects.get(user=user)
                cart_items = CartItem.objects.filter(cart=cart).count()
            except:
                cart_items = 0
            data = {"access": token.key, "user_type": user_type, "user_name": user.username, "email": user.email, "total_items": cart_items}
            return Response({
                "status": "1",
                "message": "Success",
                "Data": data
            })
        else:
            return Response({
                "status": "1",
                "message": "Success",
                "Data": data
            })
        
    def merge_cart(self, user):
        session_id = self.request.session.session_key
        anonymous_cart = Cart.objects.filter(session_id=session_id, user=None).first()

        if anonymous_cart:
            user_cart, _ = Cart.objects.get_or_create(user=user)

            # Move items from the anonymous cart to the user's cart
            for item in CartItem.objects.filter(cart=anonymous_cart):
                cart_item, cart_created = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                # cart_item.quantity += item.quantity
                cart_item.quantity = item.quantity if cart_created else cart_item.quantity + item.quantity
                cart_item.save()

            anonymous_cart.delete()

    def merge_wishlist(self, user):
        session_id = self.request.session.session_key
        anonymous_wishlist = Wishlist.objects.filter(session_id=session_id, user=None).first()

        if anonymous_wishlist:
            user_wishlist, _ = Wishlist.objects.get_or_create(user=user)

            # Move items from the anonymous cart to the user's cart
            for item in WishlistItem.objects.filter(wishlist=anonymous_wishlist):
                wishlist_item, wishlist_created = WishlistItem.objects.get_or_create(wishlist=user_wishlist, product=item.product)
                # cart_item.quantity += item.quantity
                # cart_item.quantity = item.quantity if cart_created else cart_item.quantity + item.quantity
                # cart_item.save()

            anonymous_wishlist.delete()

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Delete the token associated with the current user
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Successfully logged out."})
    


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        # Fetch the profile of the currently logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get(self, request, *args, **kwargs):
        # This method will return the profile of the currently logged-in user
        profile = self.get_object()
        serializer = ProfileSerializer(profile)
        return Response({"Status": "1", "message": "Success", "Data": [serializer.data]}, status=status.HTTP_200_OK)

    # def put(self, request, *args, **kwargs):
    #     profile = self.get_object()
    #     serializer = self.get_serializer(profile, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"Status": "1", "message": "Success", "Data": [serializer.data]})

    def perform_update(self, serializer):
        # Custom logic (if needed) before saving
        serializer.save()


class CustomerSignupView(APIView):
    def post(self, request):
        email = request.data["email"]
        try:
            tempuser = TemporaryUserContact.objects.get(email=email)
            if tempuser:
                tempuser.delete()
        except:
            print("No data")
        serializer = CustomerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SellerSignupView(APIView):
    def post(self, request):
        serializer = SellerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Seller account created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
        serializer = ProductSerializer(fast_moving_products, many=True)
        return Response({"Status": "1", "message": "Success", "Data": serializer.data})
    




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
        


class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)

        # Prepare the cart items data
        items = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None  # Choose the first image or None if no image
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_images': f"/media/{product_image}" if product_image != None else None,
                'quantity': item.quantity,
                'price_per_item': item.product.price,
                'delivery_charge': item.product.delivery_charge,
                'min_order_quantity': item.product.min_order_quantity,
                'min_order_quantity_two': item.product.min_order_quantity_two,
                'min_order_quantity_three': item.product.min_order_quantity_three,
                'min_order_quantity_four': item.product.min_order_quantity_four,
                'min_order_quantity_five': item.product.min_order_quantity_five,
                'total_price': item.quantity * item.product.price,
                'created_at': item.created_at,
                'updated_at': item.updated_at
            })

        return Response({
            'Status': '1',
            'cart_id': cart.id,
            'total_items': len(items),
            'items': items,
        }, status=status.HTTP_200_OK)  
    

    def post(self, request):
        product_id = request.data.get('product_id')

        # Debugging print statements
        print(f"Request data: Product ID = {product_id}")

        if not product_id:
            return Response({'Status': '0', 'message': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # Debugging print statement
        print(f"User ID: {user.id}")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Debugging print statement
        print(f"Product ID: {product.id}, Stock: {product.stock}")

        # Use product's minimum order quantity as the default quantity
        quantity = 1

        if product.stock < int(quantity):
            return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=user)
        # Debugging print statement
        print(f"Cart ID: {cart.id}, Created: {created}")

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        # Debugging print statement
        print(f"Cart Item: {cart_item}, Created: {created}")

        if created:
            cart_item.quantity = int(quantity)
        else:
            if cart_item.quantity + int(quantity) > product.stock:
                return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += int(quantity)

        cart_item.save()

        # Update the product stock
        product.stock -= int(quantity)
        if product.stock < 0:
            return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        product.save()

        return Response({"Status": "1", "message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'Status': '0', 'message': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # If found, delete the cart item
        cart_item.delete()

        return Response({"Status": "1", "message": "Item removed from cart successfully"}, status=status.HTTP_200_OK)
    

class UpdateCart(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock + cart_item.quantity < int(quantity):
            return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        # Adjust the stock
        product.stock += cart_item.quantity - int(quantity)
        product.save()

        # Update the cart item quantity
        cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = ProductSerializer(product)
        product_data = serializer.data
        product_data['quantity'] = cart_item.quantity
        print("ddd", product_data)
        if cart_item.quantity < product.min_order_quantity:
            delivery_charge = product.delivery_charge
            products = Product.objects.filter(vendor=user)
            # serializer = ProductSerializer(product)
            return Response({
                "Status": "1",
                "message": "Cart updated successfully",
                "delivery_charge": delivery_charge,
                "info": f"You need to pay a delivery charge of {delivery_charge} as the quantity is less than the minimum order quantity.",
                "Data": [product_data]
            }, status=status.HTTP_200_OK)
        
        # If no delivery charge
        return Response({
            "Status": "1",
            "message": "Cart updated successfully",
            "delivery_charge": 0.0,
            "Data": [product_data]
        }, status=status.HTTP_200_OK)


class DeliveryAddressListCreateView(ListCreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # def get_queryset(self):
    #     # Get only the delivery addresses of the authenticated user
    #     return DeliveryAddress.objects.filter(user=self.request.user)

    def get_queryset(self):
        # Get only the delivery addresses of the authenticated user
        user = self.request.user
        profile = Profile.objects.get(user=user)
        
        # Get the default address and remaining addresses
        default_address = profile.default_address
        addresses = DeliveryAddress.objects.filter(user=user).exclude(id=default_address.id if default_address else None)
        print(addresses)
        if default_address:
            return DeliveryAddress.objects.filter(id=default_address.id).union(addresses)
        else:
            return addresses

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"Status": "1", "message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            delivery_address = serializer.save(user=self.request.user)
            profile = Profile.objects.get(user=self.request.user)
            if profile.default_address is None:
                # If no default address, set this new address as the default
                profile.default_address = delivery_address
                profile.save()
            # self.perform_create(serializer)
            return Response({"Status": "1", "message": "Address added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"Status": "0", "message": "Failed to add address", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # def perform_create(self, serializer):
    #     # Set the user of the delivery address to the authenticated user
    #     serializer.save(user=self.request.user)



class DeliveryAddressDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        # Ensure that users can only interact with their own addresses
        return DeliveryAddress.objects.filter(user=self.request.user).order_by('-is_default', '-id')

    def get_object(self):
        # Retrieve the address and check if it belongs to the current user
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this address.")
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"Status": "1", "message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"Status": "1", "message": "Address updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"Status": "0", "message": "Failed to update address", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Status": "1", "message": "Address deleted successfully"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


# class PlaceOrderView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     def post(self, request):
#         serializer = CustomerOrderSerializer(data=request.data)
#         if serializer.is_valid():
#             order = serializer.save(user=request.user)
            
#             # Handle multiple products from cart or single product
#             if 'cart_items' in request.data:
#                 # If called from the cart, process all cart items
#                 for item_data in request.data.get('cart_items', []):
#                     item_data['order'] = order.id
#                     item_serializer = OrderItemSerializer(data=item_data)
#                     if item_serializer.is_valid():
#                         item_serializer.save()
#             else:
#                 # Single product "Buy Now" scenario
#                 product_id = request.data.get('product_id')
#                 quantity = request.data.get('quantity')

#                 try:
#                     product = Product.objects.get(id=product_id)
#                 except Product.DoesNotExist:
#                     return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
                
#                 # Use min_order_quantity if quantity is not provided
#                 if not quantity:
#                     quantity = product.min_order_quantity

#                 item_data = {
#                     'order': order.id,
#                     'product': product_id,
#                     'quantity': quantity,
#                     'price': product.price,
#                 }
#                 item_serializer = OrderItemSerializer(data=item_data)
#                 if item_serializer.is_valid():
#                     item_serializer.save()
            
#             return Response({"Status": "1", "message": "Success"}, status=status.HTTP_201_CREATED)

#         return Response({"Status": "0", "message": "Failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DefaultDeliveryAddressView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # GET method to retrieve the default address
    def get(self, request):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
            try:
                default_address = profile.default_address
                print("sss",default_address)
            except:
                return Response({"Status": "0", "message": "No default address found"}, status=status.HTTP_404_NOT_FOUND)
            
            # default_address = DeliveryAddress.objects.get(user=user, is_default=True)
            if default_address != None:
                delivery_address_serializer = DeliveryAddressSerializer(default_address)
                return Response({"Status": "1", "message": "Success", "data": [delivery_address_serializer.data]}, status=status.HTTP_200_OK)
            else:
                return Response({"Status": "0", "message": "No default address found"}, status=status.HTTP_404_NOT_FOUND)
        except DeliveryAddress.DoesNotExist:
            return Response({"Status": "0", "message": "No user found"}, status=status.HTTP_404_NOT_FOUND)

    # POST method to set a new default address
    def post(self, request):
        user = request.user
        new_default_address_id = request.data.get('default_address')  # Get the ID of the new default address

        # Unmark the current default address
        # try:
        #     DeliveryAddress.objects.filter(user=user, is_default=True).update(is_default=False)
        # except DeliveryAddress.DoesNotExist:
        #     return Response({"Status": "0", "message": "No default address found to unmark"}, status=status.HTTP_404_NOT_FOUND)

        # Mark the new address as default
        try:
            new_default_address = DeliveryAddress.objects.get(id=new_default_address_id, user=user)  # Fetch the new default address
            # new_default_address.is_default = True
            # new_default_address.save()
        except DeliveryAddress.DoesNotExist:
            return Response({"Status": "0", "message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(user=user)
        profile.default_address = new_default_address
        profile.save()
        delivery_address_serializer = DeliveryAddressSerializer(new_default_address)
        return Response({"Status": "1", "message": "Default address updated successfully", "data": delivery_address_serializer.data}, status=status.HTTP_200_OK)

    

class Checkout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user

        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'No items in the cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)
        data = []
        total_delivery_charge = []
        total_price = []
        actual_price = []
        offer_price = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None
            total_delivery_charge.append(item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0)
            total_price.append(item.product.price * item.quantity)
            actual_price.append(item.product.actual_price * item.quantity)
            offer_price.append(item.product.price * item.quantity)
            data.append({
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                'product_images': f'/media/{product_image}' if product_image != None else None,
                'quantity': item.quantity,
                "offer_percent": item.product.offer_percent,
                "actual_price": item.product.actual_price,
                "delivery_charge": item.product.delivery_charge
            })
        return Response({"Status": "1", "message": "Success", "Data": data, "delivery_charge": 0.0 if sum(total_delivery_charge) == 0 else sum(total_delivery_charge), "actual_prices": sum(actual_price), "offer_price": sum(offer_price), "total_price": sum(total_price) + sum(total_delivery_charge)}, status=status.HTTP_200_OK)
    



def get_cart_item(request):
        user = request.user

        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'No items in the cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)
        data = []
        total_delivery_charge = []
        total_price = []
        actual_price = []
        offer_price = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None
            total_delivery_charge.append(item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0)
            total_price.append(item.product.price * item.quantity)
            actual_price.append(item.product.actual_price * item.quantity)
            offer_price.append(item.product.price * item.quantity)
            data.append({
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                'product_images': product_image,
                'quantity': item.quantity,
                "offer_percent": item.product.offer_percent,
                "actual_price": item.product.actual_price,
                "delivery_charge": item.product.delivery_charge
            })
        return {"delivery_charge": sum(total_delivery_charge), "actual_prices": sum(actual_price), "offer_price": sum(offer_price), "total_price": sum(total_price) + sum(total_delivery_charge)}




class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, format=None):
        user = request.user  # Assuming the user is authenticated

        full_cart = get_cart_item(request)
        print("dsdsd", full_cart['delivery_charge'])
        profile = Profile.objects.get(user=user)
        delivery_address = profile.default_address

        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
        except:
            return Response({"Status": "0", "message": "No cart Found"})
        
        if cart_items:
        
            # Generate a unique order number
            order_number = get_random_string(length=15)

            # Creating the order
            order = CustomerOrder.objects.create(
                user=user,
                # status='1',  # Ordered
                total_price= full_cart['offer_price'],  # Set any dummy price or calculate from cart
                delivery_charge= full_cart['delivery_charge'],  # Dummy delivery charge
                net_total= full_cart['total_price'],  # Total price + delivery charge
                payment_type='COD',  # Dummy payment type
                order_number=order_number,
                delivery_address=delivery_address,
                payment_status='Pending'
            )

            # Create Order Items with images
            products = Product.objects.all()  # Fetch some products (you can change logic here)

            for item in cart_items:
                # quantity = item.quantity  # Example quantity
                order_item = OrderItem.objects.create(
                    order=order,
                    status='1',
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,  # Use product price or custom price
                )

                # Example logic to associate images (you can modify this as needed)
                for img in item.product.product_images.all():  # Assuming you have a related_name 'images' in the Product model
                    OrderProductImage.objects.create(
                        order_item=order_item,
                        image=img.image  # Use the image from the product's images
                    )
            cart_items.delete()
            # Serialize and return the order
            serializer = CustomerOrderSerializer(order)
            return Response({"Status": "1", "message": "Success", "Data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "0", "message": "No items in the cart"})


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
    

# class AllOrdersView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     def get(self, request):
#         user = request.user
#         profile = Profile.objects.get(user=user)
#         if profile.user_type == "customer":
#             try:
#                 orders = CustomerOrder.objects.filter(user=user)
#                 serializer = CustomerOrderSerializer(orders, many=True)
#                 return Response({
#                     'Status': '1',
#                     'message': "Success",
#                     "Data": serializer.data
#                 }, status=status.HTTP_200_OK)
#             except:
#                 return Response({'Status': '1', 'message': "You have no orders to view"}, status=status.HTTP_404_NOT_FOUND)




class AllOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all the orders of the logged-in user
        orders = CustomerOrder.objects.filter(user=user)

        if not orders.exists():
            return Response({
                'Status': '0',
                'message': 'No orders found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all the order items related to the user's orders
        order_items = OrderItem.objects.filter(order__in=orders)

        if not order_items.exists():
            return Response({
                'Status': '0',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Prepare response data
        response_data = []
        for item in order_items:
            product_data = ProductSerializer(item.product).data
            product_data['order_number'] = item.order.order_number
            # product_data['status'] = item.order.get_status_display()
            product_data['order_status'] = item.status
            product_data['is_approved'] = item.is_approved
            product_data['delivery_from'] = item.product.vendor.profile.address if item.product.vendor else "Unknown"
            product_data['delivery_to'] = item.order.delivery_address.city if item.order.delivery_address else "Unknown"
            product_data['delivery_date'] = item.estimated_delivery_date().strftime("%d %b %Y")
            product_data['quantity'] = item.quantity
            product_data['address'] = [{"name": item.order.delivery_address.name,
                                       "house_name": item.order.delivery_address.housename,
                                       "city": item.order.delivery_address.city,
                                       "state": item.order.delivery_address.state,
                                       "pincode": item.order.delivery_address.pincode,
                                       "mobile_number": item.order.delivery_address.mobile}]
            delivery_charge = item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0
            product_data['subtotal'] = item.quantity * item.price + delivery_charge
            product_data['payment_type'] = item.order.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)
    



class PendingOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all the orders of the logged-in user
        orders = CustomerOrder.objects.filter(user=user)

        if not orders.exists():
            return Response({
                'Status': '0',
                'message': 'No delivered orders found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all the order items related to the user's orders
        order_items = OrderItem.objects.filter(order__in=orders, is_approved=False)

        if not order_items.exists():
            return Response({
                'Status': '0',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Prepare response data
        response_data = []
        for item in order_items:
            product_data = ProductSerializer(item.product).data
            product_data['order_number'] = item.order.order_number
            product_data['order_status'] = item.status
            product_data['is_approved'] = item.is_approved
            product_data['delivery_from'] = item.product.vendor.profile.address if item.product.vendor else "Unknown"
            product_data['delivery_to'] = item.order.delivery_address.city if item.order.delivery_address else "Unknown"
            product_data['delivery_date'] = item.estimated_delivery_date().strftime("%d %b %Y")
            product_data['quantity'] = item.quantity
            product_data['address'] = [{"name": item.order.delivery_address.name,
                                       "house_name": item.order.delivery_address.housename,
                                       "city": item.order.delivery_address.city,
                                       "state": item.order.delivery_address.state,
                                       "pincode": item.order.delivery_address.pincode,
                                       "mobile_number": item.order.delivery_address.mobile}]
            delivery_charge = item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0
            product_data['subtotal'] = item.quantity * item.price + delivery_charge
            product_data['payment_type'] = item.order.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)
    

class DeliveredOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all the orders of the logged-in user
        orders = CustomerOrder.objects.filter(user=user)

        if not orders.exists():
            return Response({
                'Status': '0',
                'message': 'No delivered orders found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all the order items related to the user's orders
        order_items = OrderItem.objects.filter(order__in=orders, status="3", is_approved=True)

        if not order_items.exists():
            return Response({
                'Status': '0',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Prepare response data
        response_data = []
        for item in order_items:
            product_data = ProductSerializer(item.product).data
            product_data['order_number'] = item.order.order_number
            product_data['order_status'] = item.status
            product_data['is_approved'] = item.is_approved
            product_data['delivery_from'] = item.product.vendor.profile.address if item.product.vendor else "Unknown"
            product_data['delivery_to'] = item.order.delivery_address.city if item.order.delivery_address else "Unknown"
            product_data['delivery_date'] = item.estimated_delivery_date().strftime("%d %b %Y")
            product_data['quantity'] = item.quantity
            product_data['address'] = [{"name": item.order.delivery_address.name if item.order.delivery_address.name else None,
                                       "house_name": item.order.delivery_address.housename,
                                       "city": item.order.delivery_address.city,
                                       "state": item.order.delivery_address.state,
                                       "pincode": item.order.delivery_address.pincode,
                                       "mobile_number": item.order.delivery_address.mobile}]
            delivery_charge = item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0
            product_data['subtotal'] = item.quantity * item.price + delivery_charge
            product_data['payment_type'] = item.order.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)




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



class CategoryProductSearchView(APIView):
    def post(self, request, category_id):
        search_word = request.data.get('search_word', '')
        if search_word:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category, name__icontains=search_word)
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
    



class GetSellerOrders(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            order_items = OrderItem.objects.filter(product__vendor=user)
            print("dsadd",order_items[0].product)
            # else:
            #     # Fetch all products related to the vendor (seller)
            # serializer = ProductSerializer(products, many=True)
            # print(serializer)
            data = []
            for item in order_items:
                data.append({
                    "name": item.product.name,
                    "price": item.product.price,
                    "quantity": item.quantity,
                    "delivery_from": item.order.delivery_address.city
                })
            # return Response({'Status: 1', 'message': 'Success', })
            return Response({'Status': '1', 'message': 'Success', 'Data': data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)



class WishlistView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)

        # Prepare the cart items data
        items = []
        for item in wishlist_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None  # Choose the first image or None if no image
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_images': f"/media/{product_image}" if product_image != None else None,
                'price_per_item': item.product.price,
                'delivery_charge': item.product.delivery_charge,
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

    # def get(self, request):
    #     # Get or create the user's wishlist
    #     wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    #     # Serialize and return the wishlist items
    #     serializer = WishlistSerializer(wishlist)
    #     return Response({
    #         'Status': '1',
    #         'Message': 'Success',
    #         'Data': [serializer.data]
    #     }, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        
        if not product:
            return Response({
                'Status': '0',
                'Message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Add the product to the wishlist
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

        return Response({
            'Status': '1',
            'Message': 'Product added to wishlist'
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        # Get the user's wishlist
        wishlist = Wishlist.objects.filter(user=request.user).first()

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
    def post(self, request):
        product_id = request.data.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        
        if not product:
            return Response({
                'Status': '0',
                'Message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Add the product to the wishlist
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        cart_item = CartItem.objects.get(product=product)
        cart_item.delete()

        return Response({
            'Status': '1',
            'Message': 'Product added to wishlist'
        }, status=status.HTTP_201_CREATED)
    




class SuperAdminContactView(APIView):
    def get(self, request):
        contacts = SuperAdmin.objects.all()
        contact_list = []

        for contact in contacts:
            contact_list.append({
                'purpose': contact.purpose,
                'phone_number': contact.phone_number,
                'content': 'This is a sample content.'
            })

        return Response({
            'Status': '1',
            'message': 'Success',
            'Data': contact_list
        }, status=status.HTTP_200_OK)
    


# class SimpleProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     def get(self, request):
#         user = request.user
#         profile = Profile.objects.get(user=user)
#         data = {
#             "username": user.username,
#             "mobile": profile.mobile_number if profile.mobile_number else ""
#         }
#         return Response({
#             'Status': '1',
#             'message': 'Success',
#             'data': [data]
#         })
    


# class TemporaryUserCreateView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         mobile = request.data.get('mobile_number')

#         # Basic validation to ensure email and mobile are provided
#         if not email or not mobile:
#             return Response({
#                 'Status': '0',
#                 'message': 'Email and mobile number are required.'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Check if email or mobile already exists in TemporaryUserContact
#         if TemporaryUserContact.objects.filter(email=email).exists():
#             return Response({
#                 'Status': '0',
#                 'message': 'Email already exists.'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         if TemporaryUserContact.objects.filter(mobile_number=mobile).exists():
#             return Response({
#                 'Status': '0',
#                 'message': 'Mobile number already exists.'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Create the temporary user contact
#             TemporaryUserContact.objects.create(email=email, mobile_number=mobile)
#         except ValidationError as e:
#             return Response({
#                 'Status': '0',
#                 'message': f'Validation error: {str(e)}'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         return Response({
#             'Status': '1',
#             'message': 'Success'
#         }, status=status.HTTP_201_CREATED)


    
class ProductMinimumQuantityView(APIView):
    def get(self, request):
        try:
            product_id = request.data["product_id"]
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
        







class UpdateCart(APIView):
    # Remove permission_classes for unauthenticated access
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is authenticated
        user = request.user if request.user.is_authenticated else None

        # If authenticated, get the cart by user
        if user:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If not authenticated, get the cart by session ID
            session_id = request.session.session_key
            cart = Cart.objects.filter(session_id=session_id).first()
            if not cart:
                return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check for existing cart item
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate stock availability
        # if product.stock + cart_item.quantity < int(quantity):
            # return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        # Adjust the stock
        # product.stock += cart_item.quantity - int(quantity)
        # product.save()

        # Update the cart item quantity
        cart_item.quantity = int(quantity)
        cart_item.save()

        # Prepare response data
        serializer = ProductSerializer(product)
        product_data = serializer.data
        product_data['quantity'] = cart_item.quantity

        if cart_item.quantity < product.min_order_quantity:
            delivery_charge = product.delivery_charge
            return Response({
                "Status": "1",
                "message": "Cart updated successfully",
                "delivery_charge": delivery_charge,
                "info": f"You need to pay a delivery charge of {delivery_charge} as the quantity is less than the minimum order quantity.",
                "Data": [product_data]
            }, status=status.HTTP_200_OK)
        
        # If no delivery charge
        return Response({
            "Status": "1",
            "message": "Cart updated successfully",
            "delivery_charge": 0.0,
            "Data": [product_data]
        }, status=status.HTTP_200_OK)




@method_decorator(csrf_exempt, name='dispatch')
class CartView(APIView):
    permission_classes = [AllowAny]  # Allow access to unauthenticated users

    def get(self, request):
        user = request.user if request.user.is_authenticated else None

        # Check if the session is initialized
        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()  # Save to create a session ID

        session_id = request.session.session_key  # Get the session key
        cart = Cart.objects.filter(user=user).first() if user else Cart.objects.filter(session_id=session_id).first()

        if not cart:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)

        # Prepare the cart items data
        items = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)
            product_image = product_images[0] if product_images else None
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_images': f"/media/{product_image}" if product_image else None,
                'quantity': item.quantity,
                'price_per_item': item.product.price,
                'total_price': item.quantity * item.product.price,
            })

        return Response({
            'Status': '1',
            'cart_id': cart.id,
            'total_items': len(items),
            'items': items,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None

        # Initialize session if not set
        if not request.session.session_key:
            print("Nooooooo")
            request.session['initialized'] = True
            request.session.save()

        session_id = request.session.session_key  # Get the session key
        print(session_id)
        cart, created = Cart.objects.get_or_create(user=user) if user else Cart.objects.get_or_create(session_id=session_id)

        # Retrieve the product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # if product.stock < quantity:
        #     return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.quantity = quantity
        else:
            # if cart_item.quantity + quantity > product.stock:
                # return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += quantity

        cart_item.save()

        # Update the product stock
        # product.stock -= quantity
        # product.save()

        return Response({"Status": "1", "message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'Status': '0', 'message': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key  # Get the session key
        cart = Cart.objects.filter(user=user).first() if user else Cart.objects.filter(session_id=session_id).first()

        if not cart:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()

        return Response({"Status": "1", "message": "Item removed from cart successfully"}, status=status.HTTP_200_OK)

    def merge_cart(self, user):
        session_id = self.request.session.session_key
        # Get the anonymous cart
        anonymous_cart = Cart.objects.filter(session_id=session_id).first()

        if anonymous_cart:
            # Get or create the user's cart
            user_cart, created = Cart.objects.get_or_create(user=user)

            # Move items from the anonymous cart to the user's cart
            for item in CartItem.objects.filter(cart=anonymous_cart):
                cart_item, _ = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                cart_item.quantity += item.quantity
                cart_item.save()

            # Delete the anonymous cart
            anonymous_cart.delete()





class WishlistView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None


         # Check if the session is initialized
        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()  # Save to create a session ID

        session_id = request.session.session_key  # Get the session key
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
                'product_images': f"/media/{product_image}" if product_image != None else None,
                'price_per_item': item.product.price,
                'delivery_charge': item.product.delivery_charge,
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

        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()  # Save to create a session ID
        
        if not product:
            return Response({
                'Status': '0',
                'Message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's wishlist

        session_id = request.session.session_key  # Get the session key
        wishlist, created = Wishlist.objects.get_or_create(user=user) if user else Wishlist.objects.get_or_create(session_id=session_id)

        # Add the product to the wishlist
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

        return Response({
            'Status': '1',
            'Message': 'Product added to wishlist'
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        # Get the user's wishlist
        wishlist = Wishlist.objects.filter(user=request.user).first()

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

        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()  # Save to create a session ID
        
        if not product:
            return Response({
                'Status': '0',
                'Message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's wishlist

        session_id = request.session.session_key  # Get the session key
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
            'Message': 'Product added to wishlist'
        }, status=status.HTTP_201_CREATED)
    


class SimpleProfileView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()
        session_id = request.session.session_key
        if user:
            profile = Profile.objects.get(user=user)
            data = {
                "username": user.username,
                "mobile": profile.mobile_number if profile.mobile_number else ""
            }
        else:
            temp_details = TemporaryUserContact.objects.get(session_id=session_id)
            data = {
                "username": temp_details.email,
                "mobile": temp_details.mobile_number
            }
        
        return Response({
            'Status': '1',
            'message': 'Success',
            'data': [data]
        })
    


class TemporaryUserCreateView(APIView):
    def post(self, request):
        email = request.data.get('email')
        mobile = request.data.get('mobile_number')

        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()
        session_id = request.session.session_key

        # Basic validation to ensure email and mobile are provided
        if not email or not mobile:
            return Response({
                'Status': '0',
                'message': 'Email and mobile number are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if email or mobile already exists in TemporaryUserContact
        if TemporaryUserContact.objects.filter(email=email).exists():
            return Response({
                'Status': '1',
                'message': 'Success'
            }, status=status.HTTP_200_OK)

        if TemporaryUserContact.objects.filter(mobile_number=mobile).exists():
            return Response({
                'Status': '1',
                'message': 'Success'
            }, status=status.HTTP_200_OK)

        try:
            # Create the temporary user contact
            TemporaryUserContact.objects.create(email=email, mobile_number=mobile, session_id=session_id)
        except ValidationError as e:
            return Response({
                'Status': '0',
                'message': f'Validation error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'Status': '1',
            'message': 'Success'
        }, status=status.HTTP_201_CREATED)