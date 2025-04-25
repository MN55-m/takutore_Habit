from django.contrib import admin
from django.urls import path
from app_video.views import video_register, video_list

app_name = 'app_video'

urlpatterns = [
    path('register/', video_register, name='video_register'),
    path('list/', video_list, name='video_list'),
]