from email import message
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from accounts.models import UserProfile
from .models import Task
from projects.models import Project


@login_required
def task_list_view(request):
    # Get user profile (needed for your model relationships)
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Filter tasks by user
    tasks = Task.objects.filter(user=user_profile)

    # Filter by status
    status = request.GET.get('status')
    if status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'incomplete':
        tasks = tasks.filter(completed=False)

    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)

    # Filter by project
    project_id = request.GET.get('project_id')
    if project_id:
        tasks = tasks.filter(project_id=project_id)

    # Search functionality
    search = request.GET.get('search')  # Fixed: added quotes
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # Sort by due date or creation date
    sort = request.GET.get('sort', '-created_at')  
    tasks = tasks.order_by(sort)

    # Get user projects for filter dropdown
    user_projects = Project.objects.filter(
        Q(user=user_profile) | Q(members=user_profile) 
    ).distinct()

    # Calculate task statistics for template
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = tasks.filter(completed=False).count()

    # Priority statistics
    high_priority = tasks.filter(priority='high').count()
    medium_priority = tasks.filter(priority='medium').count()
    low_priority = tasks.filter(priority='low').count()

    # Weekly completion data (last 7 days)
    from datetime import timedelta
    from django.utils import timezone

    weekly_data = []
    weekly_labels = []

    for i in range(6, -1, -1):  # Last 7 days (6 days ago to today)
        date = timezone.now().date() - timedelta(days=i)
        completed_count = Task.objects.filter(
            user=user_profile,
            completed=True,
            updated_at__date=date
        ).count()

        weekly_data.append(completed_count)
        weekly_labels.append(date.strftime('%a'))  # Mon, Tue, Wed, etc.

    # Calculate weekly total
    weekly_total = sum(weekly_data)

    # Context for template
    context = {
        'tasks': tasks,
        'user_projects': user_projects,
        'current_status': status,
        'current_priority': priority,
        'current_project': project_id,
        'search_query': search,
        'current_sort': sort,
        'priority_choices': Task.PRIORITY_CHOICES,
        'active_page': 'tasks',
        # Task statistics
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        # Weekly data
        'weekly_data': weekly_data,
        'weekly_labels': weekly_labels,
        'weekly_total': weekly_total,
    }

    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail_view(request, task_id):
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    task = get_object_or_404(Task, id=task_id, user=user_profile)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_create_view(request):
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()  
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        project_id = request.POST.get('project')

        if not title:
            messages.error(request, 'Task title is required')
        else:
            task = Task.objects.create(
                title=title,
                description=description,
                priority=priority,
                user=user_profile,
                due_date=due_date if due_date else None,
                project_id=project_id if project_id else None
            )
            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('tasks:task_detail', task_id=task.id)

    # Get user's projects for dropdown
    user_projects = Project.objects.filter(
        Q(user=user_profile) | Q(members=user_profile) 
    ).distinct()

    context = {
        'user_projects': user_projects,
        'priority_choices': Task.PRIORITY_CHOICES,
        'active_page': 'tasks'
    }

    return render(request, 'tasks/task_create.html', context)


@login_required
def task_edit_view(request, task_id):
    try:
        user_profile = request.user.userprofile
        task = Task.objects.get(id=task_id, user=user_profile)
    except Task.DoesNotExist:
        messages.error(request, 'Task not found or you do not have permission to edit it.')
        return redirect('tasks:task_list')
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', task.priority)
        due_date = request.POST.get('due_date')
        project_id = request.POST.get('project')
        completed = request.POST.get('completed') == 'on'

        if not title:
            messages.error(request, 'Task title is required')
        else:
            task.title = title
            task.description = description
            task.priority = priority
            task.due_date = due_date if due_date else None
            task.project_id = project_id if project_id else None
            task.completed = completed
            task.save()

            messages.success(request, f"Task '{task.title}' updated successfully!")
            return redirect('tasks:task_detail', task_id=task.id)

    user_projects = Project.objects.filter(
        Q(user=user_profile) | Q(members=user_profile)
    ).distinct()

    context = {
        'task': task,
        'user_projects': user_projects,
        'priority_choices': Task.PRIORITY_CHOICES,
        'active_page': 'tasks'
    }

    return render(request, 'tasks/task_edit.html', context)



@login_required
def task_delete_view(request, task_id):
    try:
        user_profile = request.user.userprofile
        task = Task.objects.get(id=task_id, user=user_profile)
    except Task.DoesNotExist:
        messages.error(request, 'Task not found or you do not have the permission to delete this Task')
        return redirect('tasks:task_list')
    except:
        messages.error(request, 'Please complete your profile first')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f"Task {task_title} deleted successfully!")
        return redirect('tasks:task_list')
    
    context = {
        'task': task,
        'active_page': 'tasks'
    }
    return render(request, 'tasks/task_delete.html', context)

@login_required
@require_http_methods(["POST"])
def task_toggle_complete(request, task_id):
    '''AJAX view to toggle task completion status'''
    try:
        user_profile = request.user.userprofile
        task = Task.objects.get(id=task_id, user=user_profile)
    except Task.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Task not found or you do not have permission'
        })
    except:
        return JsonResponse({
            'success': False,
            'message': 'Please complete your profile first'
        })

    task.completed = not task.completed
    task.save()

    return JsonResponse({
        'success': True,
        'completed': task.completed,
        'message': f'Task marked as {"completed" if task.completed else "pending"}'
    })

@login_required
def my_task_view(request):
    '''Quick view of the user's tasks for Dashboard'''
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    pending_tasks = Task.objects.filter(user=user_profile, completed=False)[:5]
    completed_tasks = Task.objects.filter(user=user_profile, completed=True)[:5]

    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'active_page': 'tasks'
    }

    return render(request, 'tasks/my_tasks.html', context)