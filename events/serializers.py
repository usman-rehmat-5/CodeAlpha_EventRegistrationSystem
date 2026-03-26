from rest_framework import serializers

from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()
    registered_count = serializers.IntegerField(source="registration_set.count", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "location",
            "seats",
            "registered_count",
            "available_seats",
        ]

    def get_available_seats(self, obj):
        return max(obj.seats - obj.registration_set.count(), 0)


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "user", "username", "event", "event_title", "registered_at"]
        read_only_fields = ["id", "user", "username", "registered_at", "event_title"]


class RegistrationCreateSerializer(serializers.Serializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    def validate_event(self, event):
        registered_count = event.registration_set.count()
        if registered_count >= event.seats:
            raise serializers.ValidationError("No seats available for this event.")
        return event

    def validate(self, attrs):
        user = self.context["request"].user
        event = attrs["event"]

        if Registration.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError(
                {"event": "You are already registered for this event."}
            )

        return attrs

    def create(self, validated_data):
        return Registration.objects.create(
            user=self.context["request"].user,
            event=validated_data["event"],
        )
