"""
Meeting providers create online meeting links for sessions.

The provider is chosen with the MEETING_PROVIDER setting:
  - "mock":   no setup needed, returns a placeholder link (default for local dev)
  - "google": creates a Google Calendar event with a real Google Meet link

Want to add Zoom, Jitsi or Microsoft Teams? Create a new class that
implements create_meeting() and register it in PROVIDERS below.
"""
import secrets
import string
import uuid
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass
class MeetingResult:
    link: str
    external_id: str = ""


class MeetingProviderError(Exception):
    """Raised when a provider fails to create a meeting."""


class BaseMeetingProvider:
    name = "base"

    def create_meeting(self, event) -> MeetingResult:
        raise NotImplementedError


class MockMeetingProvider(BaseMeetingProvider):
    """Returns a fake, clearly-labelled link so the full flow works offline."""

    name = "mock"

    def create_meeting(self, event) -> MeetingResult:
        letters = string.ascii_lowercase

        def chunk(n):
            return "".join(secrets.choice(letters) for _ in range(n))

        code = f"{chunk(3)}-{chunk(4)}-{chunk(3)}"
        return MeetingResult(link=f"https://meet.example.com/mock/{code}", external_id=f"mock-{code}")


class GoogleMeetProvider(BaseMeetingProvider):
    """
    Creates an event on the organizer's Google Calendar with a Google Meet
    conference attached, and returns the Meet link.

    Setup instructions: docs/GOOGLE_MEET_SETUP.md
    """

    name = "google"
    scopes = ["https://www.googleapis.com/auth/calendar.events"]

    def _service(self):
        missing = [
            key
            for key in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN")
            if not getattr(settings, key, "")
        ]
        if missing:
            raise ImproperlyConfigured(f"Google Meet provider is missing settings: {', '.join(missing)}")

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise ImproperlyConfigured(
                "Google libraries are not installed. Run: pip install -r requirements-google.txt"
            ) from exc

        credentials = Credentials(
            token=None,
            refresh_token=settings.GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.scopes,
        )
        return build("calendar", "v3", credentials=credentials, cache_discovery=False)

    def create_meeting(self, event) -> MeetingResult:
        body = {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": event.starts_at.isoformat(), "timeZone": settings.TIME_ZONE},
            "end": {"dateTime": event.ends_at.isoformat(), "timeZone": settings.TIME_ZONE},
            "conferenceData": {
                "createRequest": {
                    "requestId": uuid.uuid4().hex,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }
        try:
            created = (
                self._service()
                .events()
                .insert(calendarId=settings.GOOGLE_CALENDAR_ID, body=body, conferenceDataVersion=1)
                .execute()
            )
        except ImproperlyConfigured:
            raise
        except Exception as exc:  # googleapiclient raises several error types
            raise MeetingProviderError(f"Google Calendar API error: {exc}") from exc

        link = created.get("hangoutLink")
        if not link:
            entry_points = created.get("conferenceData", {}).get("entryPoints", [])
            link = next((ep["uri"] for ep in entry_points if ep.get("entryPointType") == "video"), "")
        if not link:
            raise MeetingProviderError("Google created the event but returned no Meet link.")
        return MeetingResult(link=link, external_id=created.get("id", ""))


PROVIDERS = {
    MockMeetingProvider.name: MockMeetingProvider,
    GoogleMeetProvider.name: GoogleMeetProvider,
}


def get_meeting_provider() -> BaseMeetingProvider:
    name = getattr(settings, "MEETING_PROVIDER", "mock")
    try:
        return PROVIDERS[name]()
    except KeyError as exc:
        raise ImproperlyConfigured(
            f"Unknown MEETING_PROVIDER '{name}'. Choose one of: {', '.join(PROVIDERS)}"
        ) from exc
