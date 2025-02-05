from django.contrib import admin
from django.urls import path
from app_video.views import Video_registerView, Video_listView

urlpatterns = [
    path('video_register/', Video_registerView.as_view(), name="video_register"),
    path('video_register/video_list/', Video_listView.as_view(), name="video_list"),
]
