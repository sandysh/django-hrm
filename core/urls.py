from django.urls import path
from . import views, settings_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', settings_views.settings, name='settings'),
]
