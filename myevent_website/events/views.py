from heapq import heapify
from multiprocessing import Event
from unicodedata import name
from urllib import request, response
import django
from django.shortcuts import redirect, render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from matplotlib.pyplot import text
from django.contrib import messages
from sympy import content, re
from .models import Events, Venue
from django.contrib.auth.models import User
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
# import Pagination Stuff
from django.core.paginator import Paginator


#show Events
def show_event(request, event_id):
    event = Events.objects.get(pk=event_id)
    return render(request, 'events/show_event.html',{
        "event":event
        })

#grab/show all the events that are happening in the particular venue
def venue_events(request,venue_id):
    #all the venues
    venue = Venue.objects.get(id=venue_id)
    #get the events from that venue
    events = venue.events_set.all()
    if events:
        return render(request, 'events/venue_events.html',{
        "events":events
        })
    else:
        messages.success(request, ("That Venue Has No Event At This Moment!! "))
        return redirect('admin-approval')


# create admin approval portal
def admin_approval(request):
    #get all the veunes
    venue_list  = Venue.objects.all()


    #count all the user, events and venues.
    event_count = Events.objects.all().count()
    venue_count = Venue.objects.all().count()
    user_count =  User.objects.all().count()

    event_list = Events.objects.all().order_by('-event_date')
    if request.user.is_superuser:
        if request.method == "POST":
            id_list = request.POST.getlist('boxes')
            #uncehck all the events
            event_list.update(approved=False)

            #update the database
            for x in id_list:
                Events.objects.filter(pk=int(x)).update(approved=True)
            messages.success(
                request, ("Event approval has been successfulyy updated!! "))
            return redirect('list-events')
        else:
            #pass to the page
            return render(request, 'events/admin_approval.html',
                          {"event_list": event_list,
                          "venue_list" : venue_list,
                          "event_count":event_count,
                          "venue_count": venue_count,
                          "user_count":user_count})

    else:
        messages.success(
            request, ("You are not authorize to view this page!!"))
        return redirect('home')

    return render(request, 'events/admin_approval.html')


def venue_pdf(request):
    # Create Bytestream object
    buf = io.BytesIO()
    # Create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    # lines = [
    #   "line 1 ",
    #  "line 2 ",
    # "line3",

    # ]
    # Designate the model
    venues = Venue.objects.all()
    # create blank list
    lines = []
    # Loop thu and output
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append("+++++++++++++++++++++++++++++++ ")

     # Loop thu and output
    for line in lines:
        textob.textLine(line)

    # Finish Up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    # Return Something
    return FileResponse(buf, as_attachment=True, filename="venue.pdf")


def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename = venue.txt'
    # Designate the model
    venues = Venue.objects.all()
    # create blank list
    lines = []
    # Loop thu and output
    for venue in venues:
        lines.append(
            f'{venue.name}\n {venue.address}\n {venue.zip_code}\n{venue.phone}\n {venue.web}\n\n\n\n')

    #list1 = ["This is line\n", "This is Mine\n","This is Rine\n"]
    response.writelines(lines)
    return response


def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename = venue.csv'
    # Designate the model
    venues = Venue.objects.all()
    # create a csv writer
    writer = csv.writer(response)

    # add column to the header
    writer.writerow(["Venue Name", "Address", "Zip Code",
                    "Phone", "Web Address", "Email"])

    # Loop thu and output
    for venue in venues:
        writer.writerow([venue.name, venue.address,
                        venue.zip_code, venue.phone, venue.web])

    return response


def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')


def delete_event(request, event_id):
    event_data = Events.objects.get(pk=event_id)
    if request.user == event_data.manager:
        event_data.delete()
        messages.success(request, ("Event Deleted successfully!!"))
        return redirect('list-events')
    else:
        messages.success(request, ("You are not authorize to delete event! "))
        return redirect('list-events')


def update_event(request, event_id):
    event_data = Events.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event_data)
    else:
        form = EventForm(request.POST or None, instance=event_data)

    if form.is_valid():
        form.save()
        return redirect('list-events')

    return render(request, 'events/update_event.html',
                  {'event_data': event_data, 'form': form})


def add_event(request):
    submitted = False
    if request.method == "POST":
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')

        else:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user  # logged in user
                event.save()
                return HttpResponseRedirect('/add_event?submitted=True')

    else:
        # going to page not submission of form!!
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm

        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/add_event.html', {'form': form, 'submitted': submitted})


def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None,
                     request.FILES or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')

    return render(request, 'events/update_venue.html',
                  {'venue': venue, 'form': form})


def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'events/search_venues.html', {'searched': searched, 'venues': venues})
    else:
        return render(request, 'events/search_venues.html', {})


def search_events(request):
    if request.method == "POST":
        searched = request.POST['searched']
        events = Events.objects.filter(name__contains=searched)
        return render(request, 'events/search_events.html', {'searched': searched, 'events': events})
    else:
        return render(request, 'events/search_events.html', {})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)

    #get the events from that venue
    events = venue.events_set.all()
    return render(request, 'events/show_venue.html',
                  {'venue': venue,
                   'venue_owner': venue_owner,
                   'events':events})


def list_venues(request):
    venue_list = Venue.objects.all()
    p = Paginator(Venue.objects.all(), 3)
    page = request.GET.get('page')
    venues = p.get_page(page)

    nums = "a"*venues.paginator.num_pages
    return render(request, 'events/venue.html',
                  {'venue_list': venue_list,
                   'venues': venues,
                   'nums': nums})


def add_venue(request):
    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id  # logged in user
            venue.save()
            # form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')

    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/add_venue.html', {'form': form, 'submitted': submitted})


def all_events(request):
    event_list = Events.objects.all().order_by('-event_date')
    return render(request, 'events/events_list.html',
                  {'event_list': event_list})

# Create your views here.


def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = 'Saqiba'
    # convert lowercase to capital/ uper case
    month = month.capitalize()
    # convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    # create the calender
    cal = HTMLCalendar().formatmonth(year, month_number)

    # get current year
    now = datetime.now()
    current_year = now.year
    # Query the event model by date
    event_list = Events.objects.filter(
        event_date__year=year,
        event_date__month=month_number)

    time = now.strftime('%I:%M %p')
    # pass this to the context dictionary

    return render(request,
                  'events/home.html', {
                      "name": name,
                      "year": year,
                      "month": month,
                      "month_number": month_number,
                      "cal": cal,
                      "current_year": current_year,
                      "time": time,
                      "event_list": event_list, })
    # use the reference of home.html file from template/events folder here!

# creating profile page all about events


def my_events(request):
    # first your is authenticated!!
    if request.user.is_authenticated:
        me = request.user.id
        events = Events.objects.filter(attendees=me)
        return render(request, 'events/my_events.html',
                      {'events': events})
    else:
        messages.success(
            request, ("You are not authorize to view this page ! "))
        return redirect('home')
