from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme_preference', 'email_notifications', 'created_at', 'updated_at']
    list_filter = ['theme_preference', 'email_notifications', 'created_at',]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User_info', {
            'fields': ('user', 'bio', 'profile_picture')
        }),
        ('Contact_info', {
            'fields': ('phone', 'location')
        }),
        ('Preferences', {
            'fields': ('theme_preference', 'email_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )