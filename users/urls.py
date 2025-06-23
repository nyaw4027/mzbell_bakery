# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile views
    path('profile/<str:username>/', views.profile_view, name='profile'),  # Using function-based view
    # Alternative: path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),  # Using class-based view
    
    # Profile editing
    path('edit-profile/', views.profile_edit, name='profile_edit'),
    path('edit/', views.edit_profile, name='edit_profile'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('signup/', views.signup_view, name='signup'),  # You might want to remove this duplicate
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]