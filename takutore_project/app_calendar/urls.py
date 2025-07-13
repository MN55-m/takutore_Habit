from django.contrib import admin
from django.urls import path
from app_calendar.views import calendar_view, edit_day_view

app_name = 'app_calendar'

urlpatterns = [
    path('', calendar_view, name="calendar"),
    path('edit/<int:year>/<int:month>/<int:day>/', edit_day_view, name='edit_day'),
    path('edit/<int:year>/<int:month>/<int:day>/<int:record_id>', edit_day_view, name='edit_day'),
]
