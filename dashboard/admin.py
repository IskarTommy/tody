from django.contrib import admin
from .models import DashboardWidget, UserStats

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'widget_type', 'position', 'is_visible', 'created_at']
    list_filter = ['widget_type', 'is_visible', 'created_at']
    search_fields = ['user__username', 'widget_type']
    list_editable = ['position', 'is_visible']
    readonly_fields = ['created_at']

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_tasks', 'completed_tasks', 'total_projects', 'completed_projects', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['user__username']
    readonly_fields = ['last_updated']
