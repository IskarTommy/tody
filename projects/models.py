from django.db import models
from django.db.models.fields import related

class Project(models.Model):
    COLOR_CHOICES = [
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('indigo', 'Indigo'),
        ('violet', 'Violet'),
        ('black', 'Black'),
        ('white', 'White'),
        ('gray', 'Gray'),
        ('purple', 'Purple'),
        ('pink', 'Pink'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE)
    members = models.ManyToManyField('accounts.UserProfile', related_name='projects', blank=True)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title