from django.urls import path

from orders.views.customer_views import *
from orders.views.superadmin_views import *
from orders.views.seller_views import *
from orders.views.common import *

app_name = 'orders'
urlpatterns = [
    

      #common

      path('notifications/', NotificationView.as_view(), name='notifications'),
      path('notifications/mark-as-read/<int:notification_id>/', NotificationMarkAsReadView.as_view(), name='notifications-mark-as-read'),

      
      #customer
      # path('', AllOrdersView.as_view(), name='all-orders'),
      path('', OrdersListView.as_view(), name='filter-orders'),
      path('<str:order_number>/<int:product_id>/', OrderDetailView.as_view(), name='order-detail'),
      path('<str:order_number>/<int:product_id>/cancel/', CancelSingleProductOrderView.as_view(), name='cancel-single-product-order'),
      # path('pending/', PendingOrdersView.as_view(), name='pending-orders'),
      # path('delivered/', DeliveredOrdersView.as_view(), name='delivered-orders'),
      path('checkout/', Checkout.as_view(), name='order-checkout'),
      path('place-order/', PlaceOrderView.as_view(), name='place-order'),

      path('cart/', CartView.as_view(), name='add-to-cart'),
      path('update-cart/', UpdateCart.as_view(), name='update-cart'),
      path('cart-from-wishlist/', CartFromWishlistView.as_view(), name='cart-from-wishlist'),

      #seller
      path('seller/customers/', SellerTotalCustomerView.as_view(), name='total-customer'),
      path('seller/revenue/', SellerTotalRevenueView.as_view(), name='total-revenue'),
      path('seller/revenue-sales/', SellerRevenueSalesView.as_view(), name='seller-revenue-sales'),
      path('seller/', SellerTotalOrderView.as_view(), name='total-orders'),
      path('seller/all/', SellerAllOrders.as_view(), name='get-seller-orders'),
      path('seller/pending/', SellerPendingOrders.as_view(), name='get-seller-orders'),
      path('seller/confirmed/', SellerConfirmedOrders.as_view(), name='get-seller-orders'),
      path('seller/shipped/', SellerShippedOrders.as_view(), name='get-seller-orders'),
      path('seller/delivered/', SellerDeliveredOrders.as_view(), name='get-seller-orders'),
      path('seller/change-status/', ChangeOrderStatus.as_view(), name='change-order-status'),
      path('seller/sales-by-year/', SellerSalesByYearView.as_view(), name='seller-sales-by-year'),
      path('seller/monthly-revenue/', SellerMonthlyRevenueView.as_view(), name='seller-monthly-revenue'),
      path('seller/satisfaction/', SellerCustomerSatisfactionView.as_view(), name='seller-customer-satisfaction'),



      #super-admin
      path('superadmin/customers/', AdminTotalCustomerView.as_view(), name='total-customer'),
      path('superadmin/revenues/', AdminTotalRevenueView.as_view(), name='total-revenue'),
      path('superadmin/', AdminTotalOrderView.as_view(), name='total-orders'),
      path('admin/revenue-sales/', AdminRevenueSalesView.as_view(), name='admin-revenue-sales'),
      path('admin/sales-by-year/', AdminSalesByYearView.as_view(), name='admin-sales-by-year'),
      path('admin/monthly-revenue/', AdminMonthlyRevenueView.as_view(), name='admin-monthly-revenue'),
      
     
]
