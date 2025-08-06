from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

class Song(models.Model):
    title = models.CharField(max_length=255)
    web_album=models.CharField(max_length=255, blank=True, null=True)
    album = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=100)
    data = models.BinaryField()
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(default=timedelta(seconds=0))
    def __str__(self):
        return self.title

