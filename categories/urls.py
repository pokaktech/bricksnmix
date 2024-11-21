from django.urls import path

from categories.views.customer_views import *
from categories.views.super_adminview import *

app_name = 'categories'
urlpatterns = [


    # if "/" is used after usertype, it is specific for them....eg: seller/signup.
    # but when "-" is used after usertype, it is not for them, but about them.
    # if no usertype, it is for customers.

    #customer
    path('', CustomerCategoryListView.as_view(), name='category-list'),
    path('<int:pk>/', CustomerCategoryDetailView.as_view(), name='category-detail'),
    path('search-product/<int:category_id>/', CategoryProductSearchView.as_view(), name='category_search'),
    path('banners/', CategoryBannerView.as_view(), name='category-banners'),



    #super_admin
    path('superadmin/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('superadmin/<int:category_id>/', CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    path('superadmin/subcategories/', SubcategoryListCreateAPIView.as_view(), name='subcategory-list-create'),
    path('superadmin/subcategories/<int:pk>/', SubcategoryRetrieveUpdateDestroyAPIView.as_view(), name='subcategory-detail'),
]
