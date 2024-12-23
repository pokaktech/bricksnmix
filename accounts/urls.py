from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from accounts.views.customer_views import *
from accounts.views.seller_views import *
from accounts.views.superadmin_views import *
from accounts.views.common import *


app_name = 'accounts'
urlpatterns = [

    # if "/" is used after usertype, it is specific for them....eg: seller/signup.
    # but when "-" is used after usertype, it is not for them, but about them.
    # if no usertype, it is for customers.

    #customer
    path('customer/signup/', CustomerSignupView.as_view(), name='customer-signup'),
    path('temporary-user-register/', TemporaryUserCreateView.as_view(), name='temporary-user-register'),

    path('login/', CustomAuthToken.as_view()),
    path('logout/', LogoutView.as_view(), name='api_logout'),

    path('simple-profile/', SimpleProfileView.as_view(), name='superadmin-contacts'),
    # path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    # path('profiles/<int:pk>/', ProfileRetrieveUpdateDestroyView.as_view(), name='profile-retrieve-update-destroy'),
    path('profile-update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('select-delivery/', DefaultDeliveryAddressView.as_view(), name='select-delivery'),
    # path('banners/', BannerListView.as_view(), name='get-banners'),
    path('create-sessionid/', CreateSessionIdView.as_view(), name='create-sessionid'),
    path('webcreate-sessionid/', WebCreateSessionIdView.as_view(), name='webcreate-sessionid'),
    path('addresses/', DeliveryAddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', DeliveryAddressDetailView.as_view(), name='address-detail'),

    path('app-feedback/create/', AppReviewCreateView.as_view(), name='app-review-create'),

    
    #Seller
    path('seller/signup/', SellerSignupView.as_view(), name='seller-signup'),
    path('seller/company/', CompanyDetailsView.as_view(), name='company'),

    #common
    path('superadmin-contacts/', SuperAdminContactView.as_view(), name='superadmin-contacts'),
    
    #superadmin
    # path('superadmin/banners/', BannerCreateView.as_view(), name='create-banners'),
    path('superadmin/brand/', AddBrandView.as_view(), name='add-brand'),
    # path('superadmin/customer-feedback/', CustomerFeedbackListView.as_view(), name='customer-feedback-list'),
    # path('superadmin/customer-feedback/overall-rating/', CustomerOverallFeedbackView.as_view(), name='customer-overall-rating'),
    # path('superadmin/seller-feedback/', SellerFeedbackListView.as_view(), name='seller-feedback-list'),
    # path('superadmin/seller-feedback/overall-rating/', SellerOverallFeedbackView.as_view(), name='seller-overall-rating'),

    path('superadmin/feedbacks/', FeedbackListView.as_view(), name='feedback-list'),
    path('superadmin/overall-app-rating/', OverallFeedbackView.as_view(), name='overall-app-rating'),


    # GET /admin/feedbacks/?user_type=seller
]
