from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import json
from django.shortcuts import get_object_or_404
from orders.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class OrderNotificationConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_group = None  # Initialize user_group to avoid AttributeError

    async def connect(self):
        # Extract token from query params or headers
        # try:
        #     token = self.scope['query_string'].decode('utf-8').split('=')[1]  # Example: ?token=abc123
        # except:
        #     token = ""
        headers = dict(self.scope.get("headers", []))
        token = None

        if b"authorization" in headers:
            auth_header = headers[b"authorization"].decode("utf-8")
            if auth_header.startswith("Token "):
                token = auth_header.split("Token ")[1]
        
        user = await self.authenticate_user(token)

        if user:
            self.user = user
            self.user_group = await self.get_user_group(user)
            print(self.user_group)
            if self.user_group:  # Ensure user group is valid
                await self.channel_layer.group_add(self.user_group, self.channel_name)
                await self.accept()
            else:
                await self.close()  # Reject the connection if the group is invalid
        else:
            print("nooo")
            await self.close()  # Reject the connection if authentication fails


    @database_sync_to_async
    def authenticate_user(self, token):
        # Replace with your token validation logic
        try:
            user = Token.objects.get(key=token)
            return user.user
        except:
            return None
        
    @database_sync_to_async
    def get_user_group(self, user):
        """Fetch user group details."""
        if hasattr(user, "profile"):
            return f"{user.profile.user_type}_{user.id}"
        return f"unknown_{user.id}"

    async def disconnect(self, close_code):
        # Ensure that user_group is not None or invalid
        if self.user_group:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        else:
            print("Invalid user group, skipping group discard.")


    async def receive(self, text_data):
        try:
            print("message:", text_data)
            data = json.loads(text_data)
            # Handle incoming messages (e.g., broadcast to a group)
            await self.channel_layer.group_send(
                self.user_group,
                {"type": "send_notification", "message": data.get("message")},
            )
        except Exception as e:
            print("This is error:", e)

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))



def store_notification(user, message):
    """Store the notification in the database."""
    Notification.objects.create(
        user=user,
        message=message,
    )


def send_message(item, order):
    channel_layer = get_channel_layer()
    user_group = f"{item.product.vendor.profile.user_type}_{item.product.vendor.id}"
    async_to_sync(channel_layer.group_send)(
        user_group,
        {"type": "send_notification", "message": f"New order placed with ID {order.order_number}"}
    )


def send_message_to_customer(user, order):
    channel_layer = get_channel_layer()
    user_group = f"{order.order.user.profile.user_type}_{order.order.user.id}"
    async_to_sync(channel_layer.group_send)(
        user_group,
        {"type": "send_notification", "message": f"Your order has confirmed {order.order.order_number}"}
    )







# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# def notify_order_status(order):
#     channel_layer = get_channel_layer()
#     user_group = f"{order.user.profile.user_type}_{order.user.id}"  # Use user type and ID
#     async_to_sync(channel_layer.group_send)(
#         user_group,
#         {"type": "send_notification", "message": f"Your order {order.id} is updated!"}
#     )
