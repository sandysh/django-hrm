from django.urls import path
from . import web_views, department_views

urlpatterns = [
    # Employee URLs
    path('', web_views.employee_list, name='employee_list'),
    path('create/', web_views.employee_create, name='employee_create'),
    path('<int:pk>/', web_views.employee_detail, name='employee_detail'),
    path('<int:pk>/edit/', web_views.employee_edit, name='employee_edit'),
    path('<int:pk>/delete/', web_views.employee_delete, name='employee_delete'),
    path('<int:pk>/sync/', web_views.employee_sync, name='employee_sync'),
    path('<int:pk>/promote/', web_views.employee_promote, name='employee_promote'),
    
    # Department URLs
    path('departments/', department_views.department_list, name='department_list'),
    path('departments/create/', department_views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', department_views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', department_views.department_delete, name='department_delete'),
    
    # Designation URLs
    path('designations/', department_views.designation_list, name='designation_list'),
    path('designations/create/', department_views.designation_create, name='designation_create'),
    path('designations/<int:pk>/edit/', department_views.designation_edit, name='designation_edit'),
    path('designations/<int:pk>/delete/', department_views.designation_delete, name='designation_delete'),
]

