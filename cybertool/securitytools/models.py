from django.db import models
from django.contrib.auth.models import User

class ScanResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_type = models.CharField(max_length=100)
    target = models.CharField(max_length=255)
    result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.scan_type} scan for {self.target}"

class PasswordAudit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)
    strength = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Password audit for {self.user.username}"