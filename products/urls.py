from django.urls import path

from products.views.customer_views import *
from products.views.superadmin_views import *
from products.views.seller_views import *


app_name = 'products'
urlpatterns = [

    # if "/" is used after usertype, it is specific for them....eg: seller/signup.
    # but when "-" is used after usertype, it is not for them, but about them.
    # if no usertype, it is for customers.

    #customer

    path('nearest-supplier/', NearestSupplierView.as_view()),
    path('nearest-supplier/<seller_id>/banners/', SpecificBannerList.as_view()),
    path('nearest-supplier/<seller_id>/special-offers/', SpecificSpecialOfferProducts.as_view()),
    path('nearest-supplier/<seller_id>/brands/', SpecificBrandListView.as_view()),

    path('', ProductDetail.as_view(), name='get-all-products'),
    path('<int:product_id>/', ProductDetail.as_view(), name='get-product-by-id'),
      
    path('trending-brands/', TrendingBrandsView.as_view(), name='get-trending-brands'),

    # path('offers/', OfferProductView.as_view(), name='get-offer-products'),
    path('banners/', BannerListView.as_view(), name='banners-list'),
    path('banners/<int:banner_id>/', BannerProductsView.as_view(), name='banner-products'),

    path('special-offers/', SpecialOfferProductsView.as_view(), name='special-offer-products'),
    path('search/special-offers/', SpecialOfferProductsSearchView.as_view(), name='search-special-offer-products'),

    path('sponsored/', CustomerSponsoredListView.as_view(), name='sponsored-list'),
    path('sponsored/<int:sponsored_id>/', CustomerSponsoredProductsView.as_view(), name='sponsored-products'),

    path('search/', ProductSearchView.as_view(), name='global_search'),
    path('search/brand/<int:brand_id>/', BrandProductSearchView.as_view(), name='brand_search'),
    path('brand/', CustomerBrandListView.as_view(), name='brand-list'),
    path('brand/<int:pk>/', CustomerBrandDetailView.as_view(), name='brand-detail'),

    path('trending/', TrendingProductAPIView.as_view(), name='trending-products'),
    path('fast-moving/', FastMovingProductsAPIView.as_view(), name='fast-moving-products'),
    path('<int:product_id>/minimum-quantity/', ProductMinimumQuantityView.as_view(), name='product-minimum-quantity'),
    path('reviews/<int:product_id>/', ProductReviewList.as_view(), name='product_reviews'),
    path('reviews/', AddProductReview.as_view(), name='add_review'),
    
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:product_id>/', WishlistView.as_view(), name='wishlist-item'),
    path('cart-wishlist/', WishListFromCartView.as_view(), name='cart-wishlist'),

    path('similar-products/<int:product_id>/', SimilarProductsView.as_view(), name='similar-products'),

    path('all-sellers/', SellerAndProducts.as_view(), name='all-sellers'),  # All sellers
    path('all-sellers/<int:seller_id>/', SellerAndProducts.as_view(), name='seller-products'),  # Seller's products

    path('top-rated/', TopRatedProductsView.as_view(), name='top-rated-products'),


    #seller
    # path('seller/<int:product_id>/stock/', ProductStockView.as_view(), name='product-stock'),
    path('seller/', ProductView.as_view(), name='product'),
    path('seller/<int:product_id>/', ProductView.as_view(), name='product'),
    path('seller/total-products/', SellerTotalProductView.as_view(), name='total-products'),
    path('seller/top-selling/', SellerTopSellingProductsAPIView.as_view(), name='top-selling-products'),

    path('seller/banners/', AddBannerView.as_view()),
    path('seller/brand/', SellerBrandView.as_view()),




    #super-admin

    path('superadmin/', AdminTotalProductView.as_view(), name='total-products'),
    path('superadmin/top-selling/', AdminTopSellingProductsAPIView.as_view(), name='top-selling-products'),




    
]
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
