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
]
