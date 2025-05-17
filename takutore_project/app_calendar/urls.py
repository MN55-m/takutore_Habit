from django.contrib import admin
from django.urls import path
from app_calendar.views import calendar_view
from . import views

app_name = 'app_calendar'

urlpatterns = [
    path("calendar/", calendar_view, name="calendar"),
    path('calendar/edit/<int:year>/<int:month>/<int:day>/', views.edit_day_view, name='edit_day'),
]
