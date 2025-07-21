from django.contrib import admin
from django.urls import path, include
from app.views import PortfolioView, SignupView, LoginView, HomeView, MypageView, MyPageEditView, PasswordChangeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PortfolioView.as_view(), name="portfolio"),
    path('takutore_Habit/signup/', SignupView.as_view(), name="signup"),
    path('takutore_Habit/login/', LoginView.as_view(), name="login"),
    path('takutore_Habit/home/', HomeView.as_view(), name="home"),
    path('takutore_Habit/home/calendar/', include('app_calendar.urls')),
    path('takutore_Habit/home/video/', include('app_video.urls')),
    path('takutore_Habit/home/workout/', include('app_workout.urls')),
    path('takutore_Habit/home/mypage/', MypageView.as_view(), name="mypage"),
    path('takutore_Habit/mypage/edit/', MyPageEditView.as_view(), name='mypage_edit'),
    path('takutore_Habit/mypage/password_change/', PasswordChangeView.as_view(), name='password_change'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
