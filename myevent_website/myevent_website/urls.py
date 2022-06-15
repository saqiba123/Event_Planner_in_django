from xml.dom.expatbuilder import DOCUMENT_NODE
from xml.dom.minidom import Document
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Configure admin site
admin.site.site_header = "My Event Planners Page"
admin.site.site_title = "Event Planners"
admin.site.index_title = " Welcome To Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('members/',include('django.contrib.auth.urls')),
    path('members/',include('members.urls')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

