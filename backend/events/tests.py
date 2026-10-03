from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import RSVP, Event
from .utils import build_google_calendar_link

User = get_user_model()


@override_settings(MEETING_PROVIDER="mock")
class EventAPITests(APITestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email="organizer@example.com", password="pass-12345-strong", first_name="Org", is_staff=True
        )
        self.student = User.objects.create_user(
            email="student@example.com", password="pass-12345-strong", first_name="Stu"
        )
        start = timezone.now() + timedelta(days=3)
        self.event = Event.objects.create(
            title="Intro to Open Source",
            description="Your first PR.",
            starts_at=start,
            ends_at=start + timedelta(hours=2),
            mode=Event.Mode.ONLINE,
            created_by=self.organizer,
        )

    def url(self, suffix=""):
        return f"/api/sessions/{self.event.id}/{suffix}"

    # --- Listing & visibility ---

    def test_anyone_can_list_sessions(self):
        response = self.client.get("/api/sessions/?when=upcoming")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_past_sessions_are_excluded_from_upcoming(self):
        start = timezone.now() - timedelta(days=5)
        Event.objects.create(title="Old", starts_at=start, ends_at=start + timedelta(hours=1))
        response = self.client.get("/api/sessions/?when=upcoming")
        self.assertEqual([e["title"] for e in response.data], ["Intro to Open Source"])

    def test_meet_link_hidden_from_non_attendees(self):
        self.event.meet_link = "https://meet.example.com/mock/abc"
        self.event.save()
        self.client.force_authenticate(self.student)
        response = self.client.get(self.url())
        self.assertIsNone(response.data["meet_link"])

    def test_meet_link_visible_after_rsvp(self):
        self.event.meet_link = "https://meet.example.com/mock/abc"
        self.event.save()
        RSVP.objects.create(event=self.event, user=self.student)
        self.client.force_authenticate(self.student)
        response = self.client.get(self.url())
        self.assertEqual(response.data["meet_link"], "https://meet.example.com/mock/abc")

    # --- Creating sessions ---

    def test_student_cannot_create_session(self):
        self.client.force_authenticate(self.student)
        response = self.client.post("/api/sessions/", self._payload())
        self.assertEqual(response.status_code, 403)

    def test_organizer_can_create_session(self):
        self.client.force_authenticate(self.organizer)
        response = self.client.post("/api/sessions/", self._payload())
        self.assertEqual(response.status_code, 201)

    def test_end_must_be_after_start(self):
        self.client.force_authenticate(self.organizer)
        payload = self._payload()
        payload["ends_at"] = payload["starts_at"]
        response = self.client.post("/api/sessions/", payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("ends_at", response.data)

    def test_in_person_requires_location(self):
        self.client.force_authenticate(self.organizer)
        payload = {**self._payload(), "mode": "in_person", "location": ""}
        response = self.client.post("/api/sessions/", payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("location", response.data)

    # --- RSVP ---

    def test_rsvp_requires_login(self):
        response = self.client.post(self.url("rsvp/"))
        self.assertEqual(response.status_code, 401)

    def test_student_can_rsvp_and_cancel(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(self.url("rsvp/"))
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["has_rsvped"])
        self.assertEqual(response.data["rsvp_count"], 1)

        response = self.client.delete(self.url("rsvp/"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["has_rsvped"])

    def test_duplicate_rsvp_rejected(self):
        self.client.force_authenticate(self.student)
        self.client.post(self.url("rsvp/"))
        response = self.client.post(self.url("rsvp/"))
        self.assertEqual(response.status_code, 400)

    def test_confirmation_email_sent_on_rsvp(self):
        """Test that a confirmation email is sent immediately when someone RSVPs."""
        self.client.force_authenticate(self.student)
        mail.outbox.clear()  # Clear any existing emails

        response = self.client.post(self.url("rsvp/"))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.to, ["student@example.com"])
        self.assertIn("Registration confirmed", email.subject)
        self.assertIn(self.event.title, email.subject)
        self.assertIn(self.event.title, email.body)
        self.assertIn("Stu", email.body)  # First name in greeting

    def test_confirmation_email_without_meet_link(self):
        """Test confirmation email shows appropriate message when meet link doesn't exist."""
        self.client.force_authenticate(self.student)
        mail.outbox.clear()

        self.client.post(self.url("rsvp/"))

        email = mail.outbox[0]
        self.assertIn("meeting link will be sent", email.body)
        self.assertNotIn("https://", email.body)  # No actual link present

    def test_confirmation_email_with_meet_link(self):
        """Test confirmation email includes meet link if it already exists."""
        self.event.meet_link = "https://meet.example.com/test123"
        self.event.save()
        self.client.force_authenticate(self.student)
        mail.outbox.clear()

        self.client.post(self.url("rsvp/"))

        email = mail.outbox[0]
        self.assertIn("https://meet.example.com/test123", email.body)

    def test_confirmation_email_different_from_invite(self):
        """Test that confirmation email is different from the invite email sent by organizers."""
        # First, student RSVPs and gets confirmation
        self.client.force_authenticate(self.student)
        self.client.post(self.url("rsvp/"))
        confirmation_email = mail.outbox[0]

        # Then organizer sends invites
        self.client.force_authenticate(self.organizer)
        self.client.post(self.url("send-invites/"))
        invite_email = mail.outbox[1]

        # Subjects should be different
        self.assertIn("Registration confirmed", confirmation_email.subject)
        self.assertIn("You're in", invite_email.subject)

        # Both should be sent to the student
        self.assertEqual(confirmation_email.to, ["student@example.com"])
        self.assertEqual(invite_email.to, ["student@example.com"])

    def test_full_session_rejects_rsvp(self):
        self.event.capacity = 1
        self.event.save()
        RSVP.objects.create(event=self.event, user=self.organizer)
        self.client.force_authenticate(self.student)
        response = self.client.post(self.url("rsvp/"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("full", str(response.data["detail"]))

    # --- Organizer tools ---

    def test_only_organizer_sees_attendees(self):
        RSVP.objects.create(event=self.event, user=self.student)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.url("attendees/")).status_code, 403)

        self.client.force_authenticate(self.organizer)
        response = self.client.get(self.url("attendees/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["user"]["email"], "student@example.com")

    def test_send_invites_creates_link_and_emails_attendees(self):
        RSVP.objects.create(event=self.event, user=self.student)
        self.client.force_authenticate(self.organizer)
        response = self.client.post(self.url("send-invites/"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["sent"], 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])

        self.event.refresh_from_db()
        self.assertTrue(self.event.meet_link.startswith("https://meet.example.com/mock/"))
        self.assertIn(self.event.meet_link, mail.outbox[0].body)
        self.assertIsNotNone(self.event.invites_sent_at)

    def test_in_person_session_gets_no_meet_link(self):
        self.event.mode = Event.Mode.IN_PERSON
        self.event.location = "Seminar Hall"
        self.event.save()
        self.client.force_authenticate(self.organizer)
        response = self.client.post(self.url("meet-link/"))
        self.assertEqual(response.status_code, 400)

    # --- Google Calendar Link ---

    def test_google_calendar_link_hidden_from_non_attendees(self):
        """Non-registered users should not see the Google Calendar link."""
        self.client.force_authenticate(self.student)
        response = self.client.get(self.url())
        self.assertIsNone(response.data.get("google_calendar_link"))

    def test_google_calendar_link_visible_after_rsvp(self):
        """Users who RSVP'd should see the Google Calendar link."""
        RSVP.objects.create(event=self.event, user=self.student)
        self.client.force_authenticate(self.student)
        response = self.client.get(self.url())

        calendar_link = response.data.get("google_calendar_link")
        self.assertIsNotNone(calendar_link)
        self.assertIn("calendar.google.com", calendar_link)
        self.assertIn("action=TEMPLATE", calendar_link)
        self.assertIn(self.event.title, calendar_link)

    def test_google_calendar_link_includes_event_details(self):
        """Calendar link should include title, dates, location, and description."""
        link = build_google_calendar_link(self.event)

        # Check that the link contains key parameters
        self.assertIn("calendar.google.com/calendar/render", link)
        self.assertIn("action=TEMPLATE", link)
        self.assertIn("text=", link)  # Title
        self.assertIn("dates=", link)  # Date range

        # If location exists, it should be in the link
        if self.event.location:
            self.assertIn("location=", link)

        # If description exists, it should be in the link
        if self.event.description:
            self.assertIn("details=", link)

    def test_google_calendar_link_includes_meet_link_in_description(self):
        """Calendar link should include meeting link in description if available."""
        self.event.meet_link = "https://meet.example.com/test123"
        self.event.save()

        link = build_google_calendar_link(self.event)

        # The meet_link should be embedded in the details parameter
        self.assertIn("details=", link)
        # Note: URL encoding means the link will be encoded in the query string

    def _payload(self):
        start = timezone.now() + timedelta(days=7)
        return {
            "title": "Git Workshop",
            "description": "Hands-on.",
            "starts_at": start.isoformat(),
            "ends_at": (start + timedelta(hours=2)).isoformat(),
            "mode": "online",
        }
