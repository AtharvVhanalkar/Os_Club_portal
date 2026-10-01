from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from .providers import GoogleMeetProvider, MockMeetingProvider, get_meeting_provider


class ProviderSelectionTests(SimpleTestCase):
    @override_settings(MEETING_PROVIDER="mock")
    def test_mock_provider_selected(self):
        self.assertIsInstance(get_meeting_provider(), MockMeetingProvider)

    @override_settings(MEETING_PROVIDER="google")
    def test_google_provider_selected(self):
        self.assertIsInstance(get_meeting_provider(), GoogleMeetProvider)

    @override_settings(MEETING_PROVIDER="carrier-pigeon")
    def test_unknown_provider_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            get_meeting_provider()

    def test_mock_link_format(self):
        result = MockMeetingProvider().create_meeting(event=None)
        self.assertTrue(result.link.startswith("https://meet.example.com/mock/"))

    @override_settings(GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET="", GOOGLE_REFRESH_TOKEN="")
    def test_google_without_credentials_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            GoogleMeetProvider()._service()
