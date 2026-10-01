from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import RSVP, Event

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

    def _payload(self):
        start = timezone.now() + timedelta(days=7)
        return {
            "title": "Git Workshop",
            "description": "Hands-on.",
            "starts_at": start.isoformat(),
            "ends_at": (start + timedelta(hours=2)).isoformat(),
            "mode": "online",
        }
