from django.contrib import admin
from django.urls import path
from app.views import PortfolioView, SignupView, LoginView, HomeView, CalendarView, Video_registerView, Video_listView, Workout_settingsView, MypageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PortfolioView.as_view(), name="portfolio"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('home/', HomeView.as_view(), name="home"),
    path('home/calendar/', CalendarView.as_view(), name="calendar"),
    path('home/video_register/', Video_registerView.as_view(), name="video_register"),
    path('home/video_register/video_list/', Video_listView.as_view(), name="video_list"),
    path('home/workout_settings/', Workout_settingsView.as_view(), name="workout_settings"),
    path('home/mypage/', MypageView.as_view(), name="mypage")
]
