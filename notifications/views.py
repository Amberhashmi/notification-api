from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer


def get_current_user(request):
    if request.user and request.user.is_authenticated:
        return request.user

    return User.objects.get_or_create(username="amber")[0]


@api_view(["GET"])
def get_notifications(request):

    user = get_current_user(request)

    notifications = Notification.objects.select_related(
        "user"
    ).filter(
        user=user
    ).order_by("-created_at")

    serializer = NotificationSerializer(
        notifications,
        many=True
    )

    return Response(serializer.data)


@api_view(["POST"])
def create_notification(request):

    user = get_current_user(request)

    message = request.data.get("message")

    duplicate = Notification.objects.filter(
        user=user,
        message=message,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).first()

    if duplicate:

        serializer = NotificationSerializer(duplicate)

        return Response(
            {
                "message": "Duplicate notification blocked",
                "notification": serializer.data
            },
            status=status.HTTP_200_OK
        )

    serializer = NotificationSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save(user=user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["PATCH"])
def mark_notification_as_read(request, id):

    user = get_current_user(request)

    try:

        notification = Notification.objects.get(
            id=id,
            user=user
        )

    except Notification.DoesNotExist:

        return Response(
            {"error": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    notification.is_read = True
    notification.save()

    serializer = NotificationSerializer(notification)

    return Response(serializer.data)