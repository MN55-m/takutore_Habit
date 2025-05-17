from django.contrib import admin
from django.urls import path
from app_workout.views import workout_settingsView, workout_menuView, save_workout_menuView

app_name = 'app_workout'

urlpatterns = [
    path('workout_settings/', workout_settingsView, name="workout_settings"),
    path('workout_menu/', workout_menuView, name="workout_menu"),
    path("workout_menu/save/", save_workout_menuView, name="save_workout_menu"),
]
