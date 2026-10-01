from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):
    """A club session: a talk, workshop, meetup or office hour."""

    class Mode(models.TextChoices):
        ONLINE = "online", "Online"
        IN_PERSON = "in_person", "In person"
        HYBRID = "hybrid", "Hybrid"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.ONLINE)
    location = models.CharField(max_length=255, blank=True, help_text="Room or address for in-person sessions.")
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Leave empty for unlimited seats.")

    meet_link = models.URLField(blank=True)
    meeting_external_id = models.CharField(max_length=255, blank=True)
    invites_sent_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title

    @property
    def needs_meet_link(self):
        return self.mode in {self.Mode.ONLINE, self.Mode.HYBRID}

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must be after the start time."})
        if self.mode in {self.Mode.IN_PERSON, self.Mode.HYBRID} and not self.location:
            raise ValidationError({"location": "In-person and hybrid sessions need a location."})


class RSVP(models.Model):
    """A member's registration for a session."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rsvps")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_rsvp_per_event"),
        ]
        verbose_name = "RSVP"
        verbose_name_plural = "RSVPs"

    def __str__(self):
        return f"{self.user} → {self.event}"
