from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.db.models import Count, Exists, OuterRef
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from meetings.providers import MeetingProviderError

from .models import RSVP, Event
from .permissions import IsOrganizer, IsOrganizerOrReadOnly
from .serializers import AttendeeSerializer, EventSerializer
from .services import ensure_meet_link, send_invites


class EventViewSet(viewsets.ModelViewSet):
    """
    Sessions API.

    GET    /api/sessions/                     list (?when=upcoming|past)
    POST   /api/sessions/                     create (organizers)
    GET    /api/sessions/{id}/                detail
    PATCH  /api/sessions/{id}/                update (organizers)
    DELETE /api/sessions/{id}/                delete (organizers)
    POST   /api/sessions/{id}/rsvp/           register for a session
    DELETE /api/sessions/{id}/rsvp/           cancel registration
    GET    /api/sessions/{id}/attendees/      list RSVPs (organizers)
    POST   /api/sessions/{id}/meet-link/      create a meeting link (organizers)
    POST   /api/sessions/{id}/send-invites/   email all RSVPs (organizers)
    """

    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

    def get_queryset(self):
        queryset = Event.objects.annotate(rsvp_count=Count("rsvps", distinct=True))

        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                user_has_rsvped=Exists(RSVP.objects.filter(event=OuterRef("pk"), user=user))
            )

        when = self.request.query_params.get("when")
        now = timezone.now()
        if when == "upcoming":
            queryset = queryset.filter(ends_at__gte=now)
        elif when == "past":
            queryset = queryset.filter(ends_at__lt=now).order_by("starts_at")
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _refreshed(self, event):
        """Re-fetch the event with annotations so counts are up to date."""
        return self.get_queryset().get(pk=event.pk)

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()

        if request.method == "DELETE":
            deleted, _ = RSVP.objects.filter(event=event, user=request.user).delete()
            if not deleted:
                return Response({"detail": "You are not registered for this session."}, status=status.HTTP_404_NOT_FOUND)
            return Response(self.get_serializer(self._refreshed(event)).data)

        if event.ends_at < timezone.now():
            raise ValidationError({"detail": "This session has already ended."})

        with transaction.atomic():
            locked = Event.objects.select_for_update().get(pk=event.pk)
            if locked.capacity is not None and locked.rsvps.count() >= locked.capacity:
                raise ValidationError({"detail": "This session is full."})
            try:
                RSVP.objects.create(event=locked, user=request.user)
            except IntegrityError:
                raise ValidationError({"detail": "You are already registered for this session."})

        return Response(self.get_serializer(self._refreshed(event)).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], permission_classes=[IsOrganizer])
    def attendees(self, request, pk=None):
        event = self.get_object()
        rsvps = event.rsvps.select_related("user")
        return Response(AttendeeSerializer(rsvps, many=True).data)

    @action(detail=True, methods=["post"], url_path="meet-link", permission_classes=[IsOrganizer])
    def meet_link(self, request, pk=None):
        event = self.get_object()
        if not event.needs_meet_link:
            raise ValidationError({"detail": "In-person sessions don't need a meeting link."})
        force = bool(request.data.get("regenerate"))
        try:
            ensure_meet_link(event, force=force)
        except (MeetingProviderError, ImproperlyConfigured) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(self.get_serializer(self._refreshed(event)).data)

    @action(detail=True, methods=["post"], url_path="send-invites", permission_classes=[IsOrganizer])
    def send_invites(self, request, pk=None):
        event = self.get_object()
        try:
            sent = send_invites(event)
        except (MeetingProviderError, ImproperlyConfigured) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({"sent": sent, "session": self.get_serializer(self._refreshed(event)).data})
