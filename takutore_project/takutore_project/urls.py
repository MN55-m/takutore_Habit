from django.contrib import admin
from django.urls import path, include
from app.views import PortfolioView, SignupView, LoginView, HomeView, MypageView, MyPageEditView, PasswordChangeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PortfolioView.as_view(), name="portfolio"),
    path('takutore_project/signup/', SignupView.as_view(), name="signup"),
    path('takutore_project/login/', LoginView.as_view(), name="login"),
    path('takutore_project/home/', HomeView.as_view(), name="home"),
    path('takutore_project/home/calendar/', include('app_calendar.urls')),
    path('takutore_project/home/video/', include('app_video.urls')),
    path('takutore_project/home/workout/', include('app_workout.urls')),
    path('takutore_project/home/mypage/', MypageView.as_view(), name="mypage"),
    path('takutore_project/mypage/edit/', MyPageEditView.as_view(), name='mypage_edit'),
    path('takutore_project/mypage/password_change/', PasswordChangeView.as_view(), name='password_change'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
