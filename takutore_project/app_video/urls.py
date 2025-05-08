from django.contrib import admin
from django.urls import path
from app_video.views import video_register, video_list, video_edit, video_delete

app_name = 'app_video'

urlpatterns = [
    path('register/', video_register, name='video_register'),  #登録
    path('list/', video_list, name='video_list'),  #一覧
    path('list/edit/<int:pk>/', video_edit, name='video_edit'),  #一覧編集
    path('list/delete/<int:pk>/', video_delete, name='video_delete'),  #一覧削除
]