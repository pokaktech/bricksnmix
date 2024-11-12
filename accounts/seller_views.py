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


from datetime import datetime, timedelta



class TotalCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            # Fetch all orders and unique customers directly from OrderItem based on the vendor
            order_items = OrderItem.objects.filter(product__vendor=user)
            print(order_items)
            # Fetch all orders containing products sold by this seller
            unique_customers = order_items.values('order__user').distinct()

            # Count the total number of unique customers
            total_customers = unique_customers.count()

            return Response({
                'Status': "1",
                'message': "Success",
                "data": [
                    {
                        "total_customers": total_customers
                    }
                ]
            })
        else:
            return Response({
                'Sttaus': '1',
                'message': "You are not a seller"
            })
        





class TotalCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            order_items = OrderItem.objects.filter(product__vendor=user)
            unique_customers = order_items.values('order__user').distinct().count()

            # Get all products belonging to the seller
            seller_products = Product.objects.filter(vendor=user)

            # Get all orders containing products sold by this seller (current month)
            current_month_start = datetime.now().replace(day=1)
            current_month_customers = (
                OrderItem.objects
                .filter(product__in=seller_products, order__created_at__gte=current_month_start)
                .values('order__user')
                .distinct()
            )
            total_customers_current = current_month_customers.count()

            # Get the previous month date range
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)

            # Get total customers for the previous month
            previous_month_customers = (
                OrderItem.objects
                .filter(
                    product__in=seller_products,
                    order__created_at__gte=previous_month_start,
                    order__created_at__lte=previous_month_end
                )
                .values('order__user')
                .distinct()
            )
            total_customers_previous = previous_month_customers.count()

            # Calculate the percentage change
            if total_customers_previous > 0:
                change_percentage = ((total_customers_current - total_customers_previous) / total_customers_previous) * 100
            else:
                change_percentage = 100 if total_customers_current > 0 else 0
            data = [{
                'total_customers': unique_customers,
                # 'total_customers_previous': total_customers_previous,
                'change_percentage': round(change_percentage, 2)
            }]
            # Prepare the response data
            response_data = {
                'Status': '1',
                'message': 'Success',
                "data": data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'Sttaus': '1',
                'message': "You are not a seller"
            })
