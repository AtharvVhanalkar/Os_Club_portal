from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import RSVP, Event
from .utils import build_google_calendar_link


class EventSerializer(serializers.ModelSerializer):
    rsvp_count = serializers.IntegerField(read_only=True)
    seats_left = serializers.SerializerMethodField()
    has_rsvped = serializers.SerializerMethodField()
    meet_link = serializers.SerializerMethodField()
    google_calendar_link = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "starts_at",
            "ends_at",
            "mode",
            "location",
            "capacity",
            "rsvp_count",
            "seats_left",
            "has_rsvped",
            "meet_link",
            "google_calendar_link",
            "invites_sent_at",
            "created_at",
        )
        read_only_fields = ("invites_sent_at", "created_at")

    def get_seats_left(self, obj):
        if obj.capacity is None:
            return None
        return max(obj.capacity - getattr(obj, "rsvp_count", 0), 0)

    def get_has_rsvped(self, obj):
        return bool(getattr(obj, "user_has_rsvped", False))

    def get_meet_link(self, obj):
        """The link is only visible to organizers and to members who RSVP'd."""
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated and (user.is_staff or self.get_has_rsvped(obj)):
            return obj.meet_link or None
        return None

    def get_google_calendar_link(self, obj):
        """Google Calendar link is only visible to users who have RSVP'd."""
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated and self.get_has_rsvped(obj):
            return build_google_calendar_link(obj)
        return None

    def validate(self, attrs):
        instance = Event(**{**self._current_values(), **attrs})
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        return attrs

    def _current_values(self):
        if not self.instance:
            return {}
        fields = ("title", "description", "starts_at", "ends_at", "mode", "location", "capacity")
        return {field: getattr(self.instance, field) for field in fields}


class AttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ("id", "user", "created_at")
