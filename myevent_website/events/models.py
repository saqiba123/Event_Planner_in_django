from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from sqlalchemy import null

from datetime import date



# Create your models here.


class Venue(models.Model):
    name = models.CharField('Venue Name', max_length=120)
    address = models.CharField(max_length=130)
    phone = models.CharField('Phone', max_length=70, blank=True)
    zip_code = models.CharField('Zip Code', max_length=40)
    web = models.URLField('Website Address', max_length=90,blank=True)
    email_address = models.EmailField('Email Address', max_length=100, blank=True)
    owner = models.IntegerField("venue Owner", blank=False,default=1)
    venue_image = models.ImageField(null=True,blank=True, upload_to="images/")

    def __str__(self):
        return self.name


class HotelUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField('User Email')
    

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Events(models.Model):
    name = models.CharField('Event Name', max_length=100)
    event_date = models.DateTimeField('Event Date')
    #venue = models.CharField(max_length=100)
    venue = models.ForeignKey(Venue, blank=True, null=True, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    attendees = models.ManyToManyField(HotelUser, blank=True)
    approved = models.BooleanField('Approved',default=False)

    def __str__(self):
        return self.name
     
    @property
    def Days_till(self):
        today = date.today()
        days_till = self.event_date.date() - today
        days_till_stripped = str(days_till).split(",",1)[0]
        return days_till_stripped

    @property
    def Is_Past(self):
        today = date.today()
        if self.event_date.date() < today:
            thing= "Past"
        else:
            thing = "Future"
        return thing