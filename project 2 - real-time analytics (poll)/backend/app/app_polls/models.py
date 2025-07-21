from django.db import models
from django.utils import timezone

# Create your models here.


class Poll(models.Model):
    question = models.CharField(max_length=255)
    text = models.JSONField()
    is_active = models.BooleanField(default=True)
    expire_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.question

    def is_expired(self):
        """
        If expire_at is None, this returns None, which evaluates to
        False in most Django filters or template conditions.
        ✅ Prevents TypeError from comparing datetime to None.
        🔐 Safe when expire_at is optional (null=True in model).
        """
        return self.expire_at and timezone.now() > self.expire_at
