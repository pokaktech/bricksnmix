from django import template
#from orders.views import Order, OrderDetails
# from orders.models import Order, OrderDetails
from orders.models import CustomerOrder, OrderItem
# from products.models import Product 
from products.models import Product
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def cart_items_count(user):
    if user.is_authenticated and not user.is_anonymous:
        if CustomerOrder.objects.all().filter(user=user, is_finished=False):
            order = CustomerOrder.objects.get(user=user, is_finished=False)
            return OrderItem.objects.all().filter(order=order).count()

        else:
            return 0



@register.filter
def underway_orders_count(user):
    if user.is_authenticated and not user.is_anonymous:
        if CustomerOrder.objects.all():
            underway_orders = OrderItem.objects.all().filter(status='0').count()
            return underway_orders

        else:
            return 0


@register.filter
def all_orders_count(user):
    if user.is_authenticated and not user.is_anonymous:
        if CustomerOrder.objects.all():
            all_order = CustomerOrder.objects.all().count()
            return all_order

        else:
            return 0


@register.filter
def all_users_count(user):
    if user.is_authenticated and not user.is_anonymous:
        if User.objects.all():
            all_users = User.objects.all().count()
            return all_users

        else:
            return 0


@register.filter
def all_products_count(user):
    if user.is_authenticated and not user.is_anonymous:
        if Product.objects.all():
            all_products = Product.objects.all().count()
            return all_products

        else:
            return 0