from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Registration
from .serializers import (
    EventSerializer,
    RegistrationCreateSerializer,
    RegistrationSerializer,
)


class RootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "message": "Event Registration System API",
            "version": "1.0",
            "endpoints": {
                "events": "/api/events/",
                "event_detail": "/api/events/<id>/",
                "register": "/api/register/",
                "user_registrations": "/api/registrations/<user_id>/",
                "cancel_registration": "/api/registrations/cancel/<registration_id>/",
                "admin": "/admin/",
            }
        })


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]


class RegisterForEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RegistrationCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        return Response(
            RegistrationSerializer(registration).data,
            status=status.HTTP_201_CREATED,
        )


class UserRegistrationListView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        if self.request.user.id != user_id and not self.request.user.is_staff:
            return Registration.objects.none()

        return Registration.objects.filter(user_id=user_id).select_related("user", "event")


class CancelRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, registration_id):
        registration = get_object_or_404(
            Registration.objects.select_related("user"),
            id=registration_id,
        )

        if registration.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to cancel this registration."},
                status=status.HTTP_403_FORBIDDEN,
            )

        registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
