from email.headerregistry import Group
from re import search
from django.contrib import admin
#import the models
from .models import Venue
from .models import HotelUser
from .models import Events
#from django.contrib.auth.models import Group



# Register your models here.

#admin.site.register(Venue, VenueAdmin)
admin.site.register(HotelUser)
#admin.site.register(Events)
#Remove group
#admin.site.unregister(Group) 

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    ordering =('name',)
    search_fields = ('name', 'address')

@admin.register(Events)
class EventAdmin(admin.ModelAdmin):
    fields = (('name', 'venue'), 'event_date', 'description', 'manager','approved')
    list_display = ('name', 'event_date', 'venue')
    list_filter = ('event_date', 'venue')
    ordering = ('-event_date',)