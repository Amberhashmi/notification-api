from django.db import models

class Notification(models.Model):
    user = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)