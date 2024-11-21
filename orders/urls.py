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

      #seller
      path('seller/customers/', SellerTotalCustomerView.as_view(), name='total-customer'),
      path('seller/revenue/', SellerTotalRevenueView.as_view(), name='total-revenue'),
      path('seller/', SellerTotalOrderView.as_view(), name='total-orders'),
      path('get-seller-orders/', GetSellerOrders.as_view(), name='get-seller-orders'),

      #super-admin
      path('superadmin/customers/', AdminTotalCustomerView.as_view(), name='total-customer'),
      path('superadmin/revenues/', AdminTotalRevenueView.as_view(), name='total-revenue'),
      path('superadmin/', AdminTotalOrderView.as_view(), name='total-orders'),

     
]
