from django.urls import path

from .views import (
    CancelRegistrationView,
    EventDetailView,
    EventListView,
    RegisterForEventView,
    UserRegistrationListView,
)


urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("register/", RegisterForEventView.as_view(), name="event-register"),
    path(
        "registrations/<int:user_id>/",
        UserRegistrationListView.as_view(),
        name="user-registrations",
    ),
    path(
        "registrations/cancel/<int:registration_id>/",
        CancelRegistrationView.as_view(),
        name="cancel-registration",
    ),
]
