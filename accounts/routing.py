from django.urls import path
from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    # re_path(r'ws/socket-server/', ConnectionConsumer.as_asgi()),
    # re_path(r'ws/client_list/', UpdateList.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]