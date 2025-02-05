from django.contrib import admin
from django.urls import path, include
from app.views import PortfolioView, SignupView, LoginView, HomeView, MypageView, MyPageEditView, PasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PortfolioView.as_view(), name="portfolio"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('home/', HomeView.as_view(), name="home"),
    path('home/', include('app_calendar.urls')),
    path('home/', include('app_video.urls')),
    path('home/', include('app_workout.urls')),
    path('home/mypage/', MypageView.as_view(), name="mypage"),
    path('mypage/edit/', MyPageEditView.as_view(), name='mypage_edit'),
    path('mypage/password_change/', PasswordChangeView.as_view(), name='password_change'),
]
