from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import CaptchaPasswordResetForm
from .views import CategoryListView,CategoryCreateView,RegisterView, LoginView,RatingReviewListCreate, RatingReviewDetail
from .views import BannerListView,TrendingBrandsView, AddBrandView, OfferProductView, ProductDetail,ProductSearchView,AddToCart, UpdateCart
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
app_name = 'accounts'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard_customer, name='dashboard_customer'),
    path('order-tracking/', views.order_tracking, name="order_tracking"),
    path('change-password/', views.change_password, name="change_password"),
    path('account_details/', views.dashboard_account_details, name="account_details"),
    path('orders-ajax/', views.MyOrdersJsonListView.as_view(),
         name='orders-ajax'),
    # 
    path('getCategories/', CategoryListView.as_view(), name='get-categories'),
    path('addCategory/', CategoryCreateView.as_view(), name='add-category'),

    path('banners/', BannerListView.as_view(), name='get-banners'),
    path('addBrand/', AddBrandView.as_view(), name='add-brand'),
    path('getTrendingBrands/', TrendingBrandsView.as_view(), name='get-trending-brands'),
    path('getOfferProducts/', OfferProductView.as_view(), name='get-offer-products'),
    path('getProductDetails/<int:product_id>/', ProductDetail.as_view(), name='get-product-by-id'),
    path('getProductDetails/', ProductDetail.as_view(), name='get-product-details'),
    path('getAllProducts/', ProductDetail.as_view(), name='get-all-products'),
    path('addProduct/', ProductDetail.as_view(), name='add-product'),
    path('getSearchedProducts/', ProductSearchView.as_view(), name='get-searched-products'),
    path('reviews/', RatingReviewListCreate.as_view(), name='review_list_create'),
    path('reviews/<int:pk>/', RatingReviewDetail.as_view(), name='review_detail'),
    path('add_to_cart/', AddToCart.as_view(), name='add_to_cart'),
    path('update_cart/', UpdateCart.as_view(), name='update_cart'),
    
    path('dashboard/order/<int:order_id>/', views.order, name='order'),


    path('password-reset/', auth_views.PasswordResetView.as_view(form_class=CaptchaPasswordResetForm, template_name='accounts/auth/password_reset.html', email_template_name='accounts/auth/password_reset_email.html',
                                                                 from_email=settings.EMAIL_SENDGRID,
                                                                 html_email_template_name='accounts/auth/password_reset_email.html',
                                                                 subject_template_name='accounts/auth/password_reset_subject.txt',
                                                                 success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/auth/password_reset_done.html'), name='password_reset_done'),
    path('password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/auth/password_reset_confirm.html',
                                                                                           post_reset_login=True, success_url=reverse_lazy('accounts:password_reset_complete')),   name='password_reset_confirm'),
    path('password-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/auth/password_reset_complete.html'), name='password_reset_complete'),
    path('download-list/', views.download_list, name="download-list"),
    path('download_file/<int:order_id>/<str:filename>/',
         views.download_file, name="download-file"),


]
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
