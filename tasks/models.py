from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related

class Task(models.Model):
    PROIRITY_CHIOCES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE,)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PROIRITY_CHIOCES, default='low')
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title