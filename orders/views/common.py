from orders.models import *
from orders.serializers import NotificationSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'Status': '1',
            'message': 'Success',
            'Data':  serializer.data
        })
    

class NotificationMarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            serializer = NotificationSerializer(notification)
            return Response({
                'Status': '1',
                'message': 'Success',
                'Data':  serializer.data
            })
        except:
            return Response({
                'Status': '1',
                'message': 'No matching Notification found'
            })


