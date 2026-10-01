# Setting up real Google Meet links

By default the portal uses a mock provider so you can develop without any setup. Organizers who run real sessions can switch to Google Meet. The portal then creates an event on the organizer's Google Calendar with a Meet link attached, and puts that link in the invite emails.

**Contributors don't need to do this.** It's only for whoever runs the live portal.

## 1. Create a Google Cloud project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project (for example, "OSC Portal").
2. Open **APIs & Services → Library**, search for **Google Calendar API** and click **Enable**.

## 2. Configure the OAuth consent screen

1. Open **APIs & Services → OAuth consent screen**.
2. Choose **External** (or **Internal** if your college uses Google Workspace and you want to keep it inside the college).
3. Fill in the app name and your email.
4. Add the scope `https://www.googleapis.com/auth/calendar.events`.
5. Under **Test users**, add the Google account that will own the meetings.

> While the app is in **Testing** mode with the External user type, Google expires refresh tokens after about 7 days, so you'd need to repeat step 4 weekly. For long-term use, publish the app or use an Internal (Workspace) app. Check Google's current documentation, as these rules can change.

## 3. Create OAuth credentials

1. Open **APIs & Services → Credentials → Create credentials → OAuth client ID**.
2. Choose **Desktop app** as the application type.
3. Download the JSON file and save it as `backend/client_secret.json`. It's already in `.gitignore`; never commit it.

## 4. Authorize and get a refresh token

```bash
cd backend
pip install -r requirements-google.txt
python manage.py google_auth client_secret.json
```

A browser window opens. Sign in with the organizer account and allow calendar access. The command prints values like:

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...
MEETING_PROVIDER=google
```

## 5. Update `.env`

Paste those values into `backend/.env` and restart Django. Optionally set `GOOGLE_CALENDAR_ID` if you want events on a calendar other than your primary one.

Create an online session, register a test account, and click **Send invites**. You should see the event on your Google Calendar and a real `meet.google.com` link in the email.

## Sending real emails

The console email backend only prints emails. To actually send them, set these in `.env`:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=club-account@gmail.com
EMAIL_HOST_PASSWORD=<app password>
DEFAULT_FROM_EMAIL=Open Source Club <club-account@gmail.com>
```

For Gmail, turn on 2-Step Verification for the account and create an **App Password** to use as `EMAIL_HOST_PASSWORD`. Personal Gmail accounts have daily sending limits, so for large clubs consider a transactional email service.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Google libraries are not installed" | `pip install -r requirements-google.txt` |
| "missing settings: GOOGLE_REFRESH_TOKEN" | Run step 4 and update `.env` |
| `invalid_grant` error | The refresh token expired or was revoked. Run step 4 again |
| Event created but no Meet link | The account may not be allowed to create Meet conferences. Try a different Google account |
