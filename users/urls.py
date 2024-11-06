from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register_view, profile_view, guest_login_view, inbox_view,
    chat_view, follow_toggle_view, notifications_view
)

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('guest-login/', guest_login_view, name='guest_login'),
    path('inbox/', inbox_view, name='inbox'),
    path('chat/<str:username>/', chat_view, name='chat'),
    # URL pour l'appel AJAX du suivi
    path('follow-toggle/', follow_toggle_view, name='follow_toggle'),
    # Ajoutez cette ligne pour les notifications
    path('notifications/', notifications_view, name='notifications'),
]
