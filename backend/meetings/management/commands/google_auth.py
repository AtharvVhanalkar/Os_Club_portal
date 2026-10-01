"""
One-time helper for organizers: authorizes the app with your Google account
and prints a refresh token to put in .env as GOOGLE_REFRESH_TOKEN.

Usage:
    python manage.py google_auth path/to/client_secret.json
"""
from django.core.management.base import BaseCommand, CommandError

from meetings.providers import GoogleMeetProvider


class Command(BaseCommand):
    help = "Authorize Google Calendar access and print a refresh token."

    def add_arguments(self, parser):
        parser.add_argument("client_secret_file", help="OAuth client JSON downloaded from Google Cloud Console")

    def handle(self, *args, **options):
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError as exc:
            raise CommandError("Run: pip install -r requirements-google.txt") from exc

        flow = InstalledAppFlow.from_client_secrets_file(options["client_secret_file"], GoogleMeetProvider.scopes)
        credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        if not credentials.refresh_token:
            raise CommandError("Google did not return a refresh token. Remove the app's access and try again.")

        self.stdout.write(self.style.SUCCESS("\nAuthorized! Add these to backend/.env:\n"))
        self.stdout.write(f"GOOGLE_CLIENT_ID={credentials.client_id}")
        self.stdout.write(f"GOOGLE_CLIENT_SECRET={credentials.client_secret}")
        self.stdout.write(f"GOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
        self.stdout.write("MEETING_PROVIDER=google\n")
        self.stdout.write(self.style.WARNING("Never commit these values to Git."))
