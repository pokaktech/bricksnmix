from django.shortcuts import render, redirect
from .forms import UserCreationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from orders.models import Order, OrderDetails
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Profile
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

# Create your views here.
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Subcategory
from .serializers import CategorySerializer
from rest_framework import status
from .models import Banner, Brand, Product, Productimg
from .serializers import BannerSerializer, BrandSerializer, OfferProductSerializer, ProductSerializer, ProductimgSerializer
# def register(request):
#     form = UserCreationForm()
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         # profile_id = request.session.get('ref_profile')
#         if form.is_valid():
#             new_user = form.save(commit=False)
#             # username = form.cleaned_data['username']
#             # email = form.cleaned_data['email']
#             new_user.set_password(form.cleaned_data['password1'])
#             new_user.save()
#             username = form.cleaned_data['username']
#             # profile_obj = Profile.objects.get(user__username=username)
#             # profile_obj.status = 'vendor'
#             # profile_obj.save()
#             # messages.success(request, f'Congratulations {username}, your account has been created')
#             messages.success(
#                 request, 'Congratulations {}, your account has been created .'.format(new_user))
#             return redirect('accounts:login')

#     return render(request, 'accounts/page-register.html', {
#         'title': 'register',
#         'form': form,
#     })



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
# def login_user(request):
    # if request.method == 'POST':
    #     form = LoginForm()
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     print(password)
    #     try:
    #         user = authenticate(request, username=User.objects.get(
    #             email=username), password=password)

    #     except:
    #         user = authenticate(request, username=username, password=password)

    #     if user is not None:
    #         login(request, user)
    #         messages.success(
    #             request, f'Welcome {username} You are logged in successfully')
    #         return redirect('accounts:dashboard_customer')

    #     else:
    #         messages.warning(request, ' username or password is incorrect')

    # else:
    #     form = LoginForm()

    # return render(request, 'accounts/page-login.html', {
    #     'title': 'Login',
    #     'form': form
    # })


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
    def get(self, request, format=None):
        products = Product.objects.filter(offer_percent__gt=0)
        serializer = OfferProductSerializer(products, many=True)
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

    # def get(self, request):
    #     product_id = request.query_params.get('product_id')
    #     if product_id:
    #         try:
    #             product = Product.objects.get(id=product_id)
    #             serializer = ProductSerializer(product)
    #             return Response({'Status': '1', 'message': 'Success', 'Data': [serializer.data]}, status=status.HTTP_200_OK)
    #         except Product.DoesNotExist:
    #             return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         products = Product.objects.all()
    #         serializer = ProductSerializer(products, many=True)
    #         return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
    
    def get(self, request, product_id=None):
        try:
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                serializer = ProductSerializer(product)
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
            else:
                products = Product.objects.all()
                serializer = ProductSerializer(products, many=True)
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        product_serializer = ProductSerializer(data=request.data,  context={'request': request})
        if product_serializer.is_valid():
            product = product_serializer.save()
            images_data = request.FILES.getlist('images')
            for image_data in images_data:
                Productimg.objects.create(product=product, image=image_data)
            return Response({"Status": "1", "message": "Product added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "0", "message": "Failed to add product", "Errors": product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(APIView):
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

class CategoryListView(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        }, status=status.HTTP_200_OK)        
        
        
class ProductSearchView(APIView):
    
    def post(self, request):
        search_word = request.data.get('search_word', '')
        if search_word:
            products = Product.objects.filter(name__icontains=search_word)
            serializer = ProductSerializer(products, many=True)
            return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'Status': '0', 'message': 'Search word not provided'}, status=status.HTTP_400_BAD_REQUEST)
        