from django.db import models
from django.contrib.auth.models import User

class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dataset {self.id} - {self.uploaded_at}"
    
    class Meta:
        ordering = ['-uploaded_at']