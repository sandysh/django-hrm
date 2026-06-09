from django.utils import timezone
from reports.models import AuditLog, logType


class AuditLogService:
    
    def __init__(self, user):
        self.user = user

    def log(self, action: logType):
        return AuditLog.objects.create(
            user=str(self.user),
            action=action,
            timestamp=timezone.now()
        )

    def login(self):
        return self.log(logType.LOGIN)

    def logout(self):
        return self.log(logType.LOGOUT)

    def create(self):
        return self.log(logType.CREATE)

    def update(self):
        return self.log(logType.UPDATE)

    def delete(self):
        return self.log(logType.DELETE)

    def email_sent(self):
        return self.log(logType.EMAIL_SENT)

    def report_generated(self):
        return self.log(logType.REPORT_GENERATED)