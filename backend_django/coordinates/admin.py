from django.contrib import admin

from coordinates.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'lon',
        'lat',
        'last_check',
    ]
    list_display_links = [
        'address',
    ]
