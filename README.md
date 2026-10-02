# Open Source Club Portal

The website for our college's Open Source Club. Organizers schedule sessions, students register, and the portal creates a meeting link and emails it to everyone who signed up.

It's also a real open source project that club members build together. If this is your first contribution anywhere, you're in the right place.

## Features

- Browse upcoming and past sessions (online, in person or hybrid)
- Create an account and register for sessions, with optional seat limits
- Organizer dashboard: create and edit sessions, see who registered
- One click to generate a meeting link and email it to every registered student
- Pluggable meeting providers: a no-setup mock provider for development and Google Meet for real sessions
- A Contributors Wall that lists everyone who has merged a pull request

## Tech stack

| Part | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Frontend | React, Vite, React Router |
| Database | SQLite (development) |
| Meetings | Google Calendar API (Google Meet links) |
| Email | Django email (console in development, SMTP in production) |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the pieces fit together.

## Getting started

You'll need **Python 3.11+**, **Node.js 20+** and **Git**.

### 1. Fork and clone

Fork this repository on GitHub, then:

```bash
git clone https://github.com/<your-username>/oss-club-portal.git
cd oss-club-portal
git remote add upstream https://github.com/<club-org>/oss-club-portal.git
git remote -v   # origin = your fork, upstream = the club's repo
```

### 2. Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
python manage.py migrate
python manage.py seed_demo       # optional: demo users and sessions
python manage.py collectstatic
python manage.py runserver
```

The API runs at http://127.0.0.1:8000/api/ and the Django admin at http://127.0.0.1:8000/admin/.

### 3. Run the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server forwards `/api` requests to Django, so both must be running.

### 4. Log in with the demo accounts

If you ran `seed_demo`:

| Role | Email | Password |
|---|---|---|
| Organizer | organizer@example.com | organizer-pass-123 |
| Student | student@example.com | student-pass-123 |

To make your own organizer account, run `python manage.py createsuperuser`.

### Emails and meeting links in development

By default, nothing is actually sent. Emails are printed in the terminal running Django, and meeting links come from the mock provider (`https://meet.example.com/mock/...`). This lets you work on every feature without any accounts or API keys.

To generate real Google Meet links, follow [docs/GOOGLE_MEET_SETUP.md](docs/GOOGLE_MEET_SETUP.md).

## Running checks

Run these before opening a pull request. CI runs them too.

```bash
# Backend
cd backend && python manage.py test

# Frontend
cd frontend && npm run lint && npm run check:contributors && npm run build
```

## Contributing

We'd love your help. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before you pick an issue, and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

Your first contribution can be adding yourself to the [Contributors Wall](frontend/src/contributors/README.md).

## License

[MIT](LICENSE)
