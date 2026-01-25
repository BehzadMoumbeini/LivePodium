from django.contrib import admin
from .models import Venue, Event

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address')
    search_fields = ('name', 'city')
    list_filter = ('city',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'date', 'venue', 'is_local')
    list_filter = ('is_local', 'date', 'venue__city')
    search_fields = ('title', 'artist')
    date_hierarchy = 'date'