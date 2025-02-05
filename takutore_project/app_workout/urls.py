from django.contrib import admin
from django.urls import path
from app_workout.views import Workout_settingsView

urlpatterns = [
    path('workout_settings/', Workout_settingsView.as_view(), name="workout_settings"),
]
