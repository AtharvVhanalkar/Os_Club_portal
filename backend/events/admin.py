from django.contrib import admin

from .models import RSVP, Event


class RSVPInline(admin.TabularInline):
    model = RSVP
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "mode", "capacity", "invites_sent_at")
    list_filter = ("mode",)
    search_fields = ("title", "description")
    inlines = [RSVPInline]


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "created_at")
    list_filter = ("event",)
