from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'priority', 'due_date', 'created_at', 'updated_at', 'completed']
    list_filter = ['priority', 'due_date', 'completed', 'created_at']
    search_fields = ['title', 'description', 'user_username']
    list_editable = ['completed', 'priority']
    readonly_fields = ['created_at', 'updated_at']

