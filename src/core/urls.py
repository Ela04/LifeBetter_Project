# src/core/urls.py
from django.contrib import admin
from django.urls import path, include
from core.views import LandingPageView, DashboardView, UserLoginView, UserLogoutView
from apps.users.views import (
    ProfileView, 
    ForumListView, 
    ForumDetailView, 
    ForumPostDeleteView 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Módulo de Perfil y Foro
    path('profile/', ProfileView.as_view(), name='profile'),
    path('forum/', ForumListView.as_view(), name='forum_list'),
    path('forum/<int:pk>/', ForumDetailView.as_view(), name='forum_detail'),
    path('forum/<int:pk>/delete/', ForumPostDeleteView.as_view(), name='forum_delete'),
    
    path('payments/', include('apps.payments.urls')),
    path('expenses/', include('apps.expenses.urls')),
]