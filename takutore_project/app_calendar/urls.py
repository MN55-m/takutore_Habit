from django.contrib import admin
from django.urls import path
from app_calendar.views import CalendarView

urlpatterns = [
    path('calendar/', CalendarView.as_view(), name="calendar"),
]
