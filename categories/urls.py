from django.urls import path

from categories.views.customer_views import *
from categories.views.super_adminview import *

app_name = 'categories'
urlpatterns = [


    # if "/" is used after usertype, it is specific for them....eg: seller/signup.
    # but when "-" is used after usertype, it is not for them, but about them.
    # if no usertype, it is for customers.

    #customer
    path('', CustomerCategoryListView.as_view(), name='category-list'), #to get all categories
    path('<int:pk>/', CustomerCategoryDetailtView.as_view(), name='category-detail'), #to get all categories

    path('<int:pk>/products/', CustomerCategoryProductView.as_view(), name='category-products'),#pass id to list all products under categories
    path('<int:category_id>/subcategory/', CustomerCategorySubCategoryView.as_view(), name='category-subcategory'),

    path('subcategories/', CustomerSubCategoryListView.as_view(), name='subcategory-list'), #to get all subcat
    path('subcategories/<int:pk>/product/', CustomerSubCategoryProductView.as_view(), name='subcategory-product'),#pass id to list all products under subcategory


    path('search-product/<int:category_id>/', CategoryProductSearchView.as_view(), name='category_search'),
    path('banners/', CategoryBannerView.as_view(), name='category-banners'), # get all cat banner



    #super_admin
    path('superadmin/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('<int:category_id>/superadmin/', CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    path('superadmin/subcategories/', SubcategoryListCreateAPIView.as_view(), name='subcategory-list-create'),
    path('superadmin/subcategories/<int:pk>/', SubcategoryRetrieveUpdateDestroyAPIView.as_view(), name='subcategory-detail'),
]
