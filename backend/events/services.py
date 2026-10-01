"""Business logic for sessions: meeting links and invitation emails."""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone

from meetings.providers import get_meeting_provider


def ensure_meet_link(event, force=False):
    """Create a meeting link for the event if it needs one and doesn't have one yet."""
    if not event.needs_meet_link:
        return event
    if event.meet_link and not force:
        return event

    result = get_meeting_provider().create_meeting(event)
    event.meet_link = result.link
    event.meeting_external_id = result.external_id
    event.save(update_fields=["meet_link", "meeting_external_id", "updated_at"])
    return event


def build_invite_email(event, user):
    context = {
        "event": event,
        "user": user,
        "event_url": f"{settings.FRONTEND_URL}/sessions/{event.id}",
        "starts_at": timezone.localtime(event.starts_at),
        "ends_at": timezone.localtime(event.ends_at),
    }
    subject = f"You're in: {event.title}"
    text_body = render_to_string("events/emails/invite.txt", context)
    html_body = render_to_string("events/emails/invite.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    return message


def send_invites(event):
    """
    Email every RSVP'd member with session details (and the meeting link for
    online/hybrid sessions). Returns the number of emails sent.
    """
    ensure_meet_link(event)
    attendees = [rsvp.user for rsvp in event.rsvps.select_related("user")]
    if not attendees:
        return 0

    messages = [build_invite_email(event, user) for user in attendees]
    with get_connection() as connection:
        sent = connection.send_messages(messages) or 0

    event.invites_sent_at = timezone.now()
    event.save(update_fields=["invites_sent_at", "updated_at"])
    return sent
