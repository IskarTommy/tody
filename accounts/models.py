from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark')

    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)

    # Dashboard theme preferences
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    email_notifications = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



#AUTO CREATE PROFILE FOR USERS

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
     """
    This function runs AFTER a User is saved to the database
    
    sender = User model (who sent the signal)
    instance = the actual User object that was just saved
    created = True if this is a NEW user, False if updating existing user
    """
     if created:
         UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    This function runs EVERY TIME a User is saved
    It makes sure the UserProfile is also saved
    """
    instance.userprofile.save()
