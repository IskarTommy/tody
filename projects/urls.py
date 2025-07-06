from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project CRUD operations
    path('', views.project_list_view, name='project_list'),
    path('<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('create/', views.project_create_view, name='project_create'),
    path('<int:project_id>/edit/', views.project_edit_view, name='project_edit'),
    path('<int:project_id>/delete/', views.project_delete_view, name='project_delete'),
    
    # Member management
    path('<int:project_id>/members/', views.project_members_view, name='project_members'),
    
    # AJAX endpoints
    path('<int:project_id>/toggle/', views.project_toggle_complete, name='project_toggle_complete'),
]
