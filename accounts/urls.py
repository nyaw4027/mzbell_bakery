
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('password/reset/', auth_views.PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password-reset-complete'),
    path('signup/', views.signup_view, name='signup'),
]