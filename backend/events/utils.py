"""Utility functions for events app."""
from urllib.parse import urlencode
from django.utils.http import urlquote


def build_google_calendar_link(event):
    """
    Build a Google Calendar 'Add to Calendar' link for an event.

    Returns a URL like:
    https://calendar.google.com/calendar/render?action=TEMPLATE&text=Event+Title&dates=...

    Args:
        event: Event model instance

    Returns:
        str: Google Calendar link
    """
    # Format dates as YYYYMMDDTHHmmssZ (UTC format for Google Calendar)
    start_time = event.starts_at.strftime('%Y%m%dT%H%M%SZ')
    end_time = event.ends_at.strftime('%Y%m%dT%H%M%SZ')

    # Build the parameters
    params = {
        'action': 'TEMPLATE',
        'text': event.title,
        'dates': f"{start_time}/{end_time}",
    }

    # Add description if exists
    if event.description:
        params['details'] = event.description

    # Add location if exists
    if event.location:
        params['location'] = event.location

    # Add meeting link to description if exists
    if event.meet_link:
        description = event.description or ""
        if description:
            description += "\n\n"
        description += f"Meeting Link: {event.meet_link}"
        params['details'] = description

    # Build the URL
    base_url = "https://calendar.google.com/calendar/render"
    query_string = urlencode(params)

    return f"{base_url}?{query_string}"
