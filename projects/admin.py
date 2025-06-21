from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'user', 'color', 'completed', 'created_at', 'updated_at']
    list_filter = ['color', 'completed', 'created_at']
    search_fields = ['title', 'description', 'user_username']
    list_editable = ['completed', 'color']
    readonly_fields = ['created_at', 'updated_at']