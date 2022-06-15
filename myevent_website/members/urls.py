from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('user_log',views.user_log, name="login" ),
    path('user_logout',views.user_logout, name="logout" ),
     path('register_user',views.register_user, name="register_user" ),
]