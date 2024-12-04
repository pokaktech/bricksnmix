from django.urls import path

from orders.views.customer_views import *
from orders.views.superadmin_views import *
from orders.views.seller_views import *

app_name = 'orders'
urlpatterns = [
      #customer
      path('', AllOrdersView.as_view(), name='all-orders'),
      path('pending/', PendingOrdersView.as_view(), name='pending-orders'),
      path('delivered/', DeliveredOrdersView.as_view(), name='delivered-orders'),
      path('checkout/', Checkout.as_view(), name='order-checkout'),
      path('place-order/', PlaceOrderView.as_view(), name='place-order'),

      path('cart/', CartView.as_view(), name='add-to-cart'),
      path('update-cart/', UpdateCart.as_view(), name='update-cart'),
      path('cart-from-wishlist/', CartFromWishlistView.as_view(), name='cart-from-wishlist'),

      #seller
      path('seller/customers/', SellerTotalCustomerView.as_view(), name='total-customer'),
      path('seller/revenue/', SellerTotalRevenueView.as_view(), name='total-revenue'),
      path('seller/', SellerTotalOrderView.as_view(), name='total-orders'),
      path('seller/all/', SellerAllOrders.as_view(), name='get-seller-orders'),
      path('seller/pending/', SellerPendingOrders.as_view(), name='get-seller-orders'),
      path('seller/confirmed/', SellerConfirmedOrders.as_view(), name='get-seller-orders'),
      path('seller/shipped/', SellerShippedOrders.as_view(), name='get-seller-orders'),
      path('seller/delivered/', SellerDeliveredOrders.as_view(), name='get-seller-orders'),
      path('notifications/', NotificationView.as_view(), name='notifications'),
      path('seller/change-status/', ChangeOrderStatus.as_view(), name='change-order-status'),

      #super-admin
      path('superadmin/customers/', AdminTotalCustomerView.as_view(), name='total-customer'),
      path('superadmin/revenues/', AdminTotalRevenueView.as_view(), name='total-revenue'),
      path('superadmin/', AdminTotalOrderView.as_view(), name='total-orders'),

     
]
