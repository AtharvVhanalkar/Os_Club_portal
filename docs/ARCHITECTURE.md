# Architecture

A quick map of the codebase so you can find your way around.

```
oss-club-portal/
├── backend/                 Django project (REST API)
│   ├── config/              settings, root URLs
│   ├── accounts/            custom User model (email login), register/login/me API
│   ├── events/              sessions and RSVPs
│   │   ├── models.py        Event and RSVP
│   │   ├── serializers.py   API representation and validation
│   │   ├── views.py         API endpoints (EventViewSet)
│   │   ├── services.py      meeting links and invite emails (business logic)
│   │   ├── templates/       email templates (text + HTML)
│   │   └── management/      seed_demo command
│   └── meetings/            pluggable meeting providers (mock, Google Meet)
├── frontend/                React app (Vite)
│   └── src/
│       ├── api/client.js    every API call lives here
│       ├── context/         logged-in user state
│       ├── components/      shared UI (header, timeline, notices)
│       ├── pages/           one file per screen; organizer/ for organizer tools
│       ├── contributors/    Contributors Wall data (one JSON file per person)
│       └── styles/          global.css with design tokens
└── docs/                    you are here
```

## How a request flows

1. The React app calls a function in `src/api/client.js`, which sends a request to `/api/...` with the user's token.
2. In development, Vite forwards `/api` to Django on port 8000.
3. Django REST Framework authenticates the token and routes to a view in `events/views.py` or `accounts/views.py`.
4. Views validate input with serializers and delegate real work to `services.py`.
5. The response comes back as JSON, and the page updates its state.

## Roles

- **Students** are regular users. They can register for and cancel sessions.
- **Organizers** are users with `is_staff = True`. They can create, edit and delete sessions, see attendees, generate meeting links and send invites. Make someone an organizer in the Django admin or with `createsuperuser`.

## API endpoints

| Method | Endpoint | Who | What |
|---|---|---|---|
| POST | `/api/auth/register/` | Anyone | Create an account, returns a token |
| POST | `/api/auth/login/` | Anyone | Log in, returns a token |
| POST | `/api/auth/logout/` | Logged in | Invalidate the token |
| GET | `/api/auth/me/` | Logged in | Current user |
| GET | `/api/sessions/?when=upcoming\|past` | Anyone | List sessions |
| POST | `/api/sessions/` | Organizer | Create a session |
| GET | `/api/sessions/{id}/` | Anyone | Session detail |
| PATCH/DELETE | `/api/sessions/{id}/` | Organizer | Update or delete |
| POST/DELETE | `/api/sessions/{id}/rsvp/` | Logged in | Register or cancel |
| GET | `/api/sessions/{id}/attendees/` | Organizer | Registered members |
| POST | `/api/sessions/{id}/meet-link/` | Organizer | Create (or regenerate) a meeting link |
| POST | `/api/sessions/{id}/send-invites/` | Organizer | Email every registered member |

The meeting link is only included in API responses for organizers and for members who registered.

## Meeting providers

`meetings/providers.py` defines a small interface:

```python
class BaseMeetingProvider:
    def create_meeting(self, event) -> MeetingResult: ...
```

The `MEETING_PROVIDER` setting chooses which one is used. To add Jitsi, Zoom or Teams, write a new class, add it to `PROVIDERS`, and add tests in `meetings/tests.py`.

## Sending invites

`events/services.py::send_invites` makes sure a meeting link exists (for online and hybrid sessions), renders `invite.txt` and `invite.html` for each attendee, sends them over a single email connection, and records `invites_sent_at`.
