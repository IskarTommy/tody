from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('reports/', views.reports_view, name='reports'),
    path('calendar/', views.calendar_view, name='calendar'),
]
