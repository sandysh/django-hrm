from django.urls import path
from . import views, settings_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', settings_views.SettingsView.as_view(), name='settings'),
    path('settings/system/', settings_views.SystemSettingsView.as_view(), name='system_settings'),
    path('settings/allowance/', settings_views.AllowanceSettingsView.as_view(), name='allowance_settings'),
    path('settings/fund/', settings_views.FundSettingsView.as_view(), name='fund_settings'),
    path('settings/tax/', settings_views.TaxSettingsView.as_view(), name='tax_settings'),
]
