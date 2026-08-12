from django.contrib import admin
from django.urls import path, include
from .views import LandingPageView, DashboardView, UserLoginView, UserLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('payments/', include('apps.payments.urls')),
]