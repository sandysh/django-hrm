from django.views import View 
from django.views.generic import ListView , TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import AuditLog, logType
from django.db.models import Q

class AuditLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AuditLog
    template_name = 'reports/audit_log_list.html'
    context_object_name = 'logs'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').order_by('-timestamp')
        
        # Filtering
        search = self.request.GET.get('search')
        action = self.request.GET.get('action')
        
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__employee_id__icontains=search)
            )
            
        if action:
            queryset = queryset.filter(action=action)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['action_filter'] = self.request.GET.get('action', '')
        context['log_types'] = logType.choices
        return context
    
    
class ReportView(LoginRequiredMixin, TemplateView):
    template_name='reports/salary_report.html'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class MailView(TemplateView):
    template_name="emails/punch_in_missing.html"