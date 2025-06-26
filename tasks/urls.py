from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task CRUD operations
    path('', views.task_list_view, name='task_list'),
    path('my-tasks/', views.my_task_view, name='my_tasks'),  # Dashboard-style view
    path('<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('create/', views.task_create_view, name='task_create'),
    path('<int:task_id>/edit/', views.task_edit_view, name='task_edit'),
    path('<int:task_id>/delete/', views.task_delete_view, name='task_delete'),

    # AJAX endpoints
    path('<int:task_id>/toggle/', views.task_toggle_complete, name='task_toggle_complete'),
]
