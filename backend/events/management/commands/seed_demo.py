"""
Creates demo data so the app isn't empty on first run.

Usage:
    python manage.py seed_demo
Creates an organizer (organizer@example.com / organizer-pass-123),
a student (student@example.com / student-pass-123) and a few sessions.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import RSVP, Event

User = get_user_model()

SESSIONS = [
    ("Your first open source contribution", "Fork, clone, branch, PR. We'll go through the full flow together.", 3, "online", "", 100),
    ("Hunting GSoC organizations", "How to filter orgs by tech stack, activity and mentor responsiveness.", 10, "hybrid", "Seminar Hall, Block A", 60),
    ("Git conflicts without fear", "Break things on purpose, then fix them.", 17, "in_person", "Lab 204", 30),
]


class Command(BaseCommand):
    help = "Seed the database with demo users and sessions."

    def handle(self, *args, **options):
        organizer, created = User.objects.get_or_create(
            email="organizer@example.com",
            defaults={"first_name": "Club", "last_name": "Organizer", "is_staff": True},
        )
        if created:
            organizer.set_password("organizer-pass-123")
            organizer.save()

        student, created = User.objects.get_or_create(
            email="student@example.com", defaults={"first_name": "Demo", "last_name": "Student"}
        )
        if created:
            student.set_password("student-pass-123")
            student.save()

        base = timezone.localtime().replace(hour=16, minute=0, second=0, microsecond=0)
        for title, description, days, mode, location, capacity in SESSIONS:
            start = base + timedelta(days=days)
            event, _ = Event.objects.get_or_create(
                title=title,
                defaults={
                    "description": description,
                    "starts_at": start,
                    "ends_at": start + timedelta(hours=2),
                    "mode": mode,
                    "location": location,
                    "capacity": capacity,
                    "created_by": organizer,
                },
            )
            if mode != "in_person":
                RSVP.objects.get_or_create(event=event, user=student)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("Organizer: organizer@example.com / organizer-pass-123")
        self.stdout.write("Student:   student@example.com / student-pass-123")
