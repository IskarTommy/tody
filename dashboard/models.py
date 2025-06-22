from django.db import models
from django.db.models.fields import related


class DashboardWidget(models.Model):
    WIDGET_TYPE = [
        ('task_summary', 'Task Summary'),
        ('recent_tasks', 'Recent Tasks'),
        ('project_progress', 'Project Progress'),
        ('upcoming_deadlines', 'Upcoming Deadlines'),
        ('completion_stats', 'Completion Statistics'),
    ]

    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPE)
    position = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']
        unique_together = ['user', 'widget_type']

    def __str__(self):
        return f"{self.user.username} - {self.get_widget_type_display()}"
    
class UserStats(models.Model):
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE)
    total_tasks = models.PositiveIntegerField(default=0)
    completed_tasks = models.PositiveIntegerField(default=0)
    total_projects = models.PositiveBigIntegerField(default=0)
    completed_projects = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def completion_rate(self):
        if self.total_tasks == 0:
            return 0
        return (self.completed_tasks / self.total_tasks) * 100
    
    def __str__(self):
        return f"{self.user.username}'s Stats"
    
    