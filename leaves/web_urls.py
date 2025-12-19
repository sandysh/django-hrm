from django.urls import path
from . import web_views, settings_views

urlpatterns = [
    path('apply/', web_views.leave_apply, name='leave_apply'),
    path('my-leaves/', web_views.my_leaves, name='my_leaves'),
    path('requests/', web_views.leave_requests, name='leave_requests'),
    path('<int:pk>/', web_views.leave_detail, name='leave_detail'),
    path('<int:pk>/approve/', web_views.leave_approve, name='leave_approve'),
    path('<int:pk>/reject/', web_views.leave_reject, name='leave_reject'),
    
    # Leave Type Management (accessed via /settings/)
    path('type/create/', settings_views.leave_type_create, name='leave_type_create'),
    path('type/<int:pk>/edit/', settings_views.leave_type_edit, name='leave_type_edit'),
    path('type/<int:pk>/delete/', settings_views.leave_type_delete, name='leave_type_delete'),
    
    # Holiday Management
    path('holidays/', web_views.holiday_calendar, name='holiday_calendar'),
    path('api/holidays/', web_views.holiday_api, name='holiday_api'),
    path('api/holidays/<int:pk>/', web_views.holiday_delete, name='holiday_delete'),
]
urlpatterns += [
    path('calendar/', web_views.user_calendar, name='user_calendar'),
    path('api/calendar/', web_views.user_calendar_api, name='user_calendar_api'),
]
