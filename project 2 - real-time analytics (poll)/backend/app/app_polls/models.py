from django.db import models

# Create your models here.


class Poll(models.Model):
    question = models.CharField(max_length=255)
    text = models.JSONField()

    def __str__(self):
        return self.question
