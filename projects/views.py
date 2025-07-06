from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods

from .models import Project
from tasks.models import Task
from accounts.models import UserProfile

@login_required
def project_list_view(request):
    """View all projects the user owns or is a member of"""
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    # Get projects where user is owner or member
    projects = Project.objects.filter(
        Q(user=user_profile) | Q(members=user_profile)
    ).distinct()
    
    # Filter by completion status
    status = request.GET.get('status')
    if status == 'completed':
        projects = projects.filter(completed=True)
    elif status == 'active':
        projects = projects.filter(completed=False)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Add task counts to each project
    for project in projects:
        project.task_count = Task.objects.filter(project=project).count()
        project.completed_task_count = Task.objects.filter(project=project, completed=True).count()
    
    context = {
        'projects': projects,
        'current_status': status,
        'search_query': search,
        'active_page': 'projects',
    }
    
    return render(request, 'projects/project_list.html', context)

@login_required
def project_detail_view(request, project_id):
    """View a specific project and its tasks"""
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    # Check if user has access to this project
    try:
        project = Project.objects.get(
            Q(id=project_id),
            Q(user=user_profile) | Q(members=user_profile)
        )
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or you do not have permission to view it.')
        return redirect('projects:project_list')
    
    # Get tasks for this project
    tasks = Task.objects.filter(project=project)
    
    # Filter tasks by completion status
    status = request.GET.get('status')
    if status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'active':
        tasks = tasks.filter(completed=False)
    
    # Get project members
    members = project.members.all()
    
    context = {
        'project': project,
        'tasks': tasks,
        'members': members,
        'is_owner': project.user == user_profile,
        'active_page': 'projects',
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_create_view(request):
    """Create a new project"""
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', 'blue')
        
        if not title:
            messages.error(request, 'Project title is required')
        else:
            project = Project.objects.create(
                title=title,
                description=description,
                color=color,
                user=user_profile
            )
            messages.success(request, f"Project '{project.title}' created successfully!")
            return redirect('projects:project_detail', project_id=project.id)
    
    context = {
        'color_choices': Project.COLOR_CHOICES,
        'active_page': 'projects'
    }
    
    return render(request, 'projects/project_create.html', context)

@login_required
def project_edit_view(request, project_id):
    """Edit an existing project"""
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    # Only the owner can edit the project
    try:
        project = Project.objects.get(id=project_id, user=user_profile)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or you do not have permission to edit it.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', 'blue')
        completed = request.POST.get('completed', '') == 'on'
        
        if not title:
            messages.error(request, 'Project title is required')
        else:
            project.title = title
            project.description = description
            project.color = color
            project.completed = completed
            project.save()
            
            messages.success(request, f"Project '{project.title}' updated successfully!")
            return redirect('projects:project_detail', project_id=project.id)
    
    context = {
        'project': project,
        'color_choices': Project.COLOR_CHOICES,
        'active_page': 'projects'
    }
    
    return render(request, 'projects/project_edit.html', context)

@login_required
def project_delete_view(request, project_id):
    """Delete a project"""
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    # Only the owner can delete the project
    try:
        project = Project.objects.get(id=project_id, user=user_profile)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or you do not have permission to delete it.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f"Project '{project_title}' deleted successfully!")
        return redirect('projects:project_list')
    
    context = {
        'project': project,
        'active_page': 'projects'
    }
    
    return render(request, 'projects/project_delete.html', context)

@login_required
def project_members_view(request, project_id):
    """Manage project members"""
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    # Only the owner can manage members
    try:
        project = Project.objects.get(id=project_id, user=user_profile)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or you do not have permission to manage members.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')
        
        if action == 'add':
            email = request.POST.get('email', '').strip()
            try:
                member = UserProfile.objects.get(user__email=email)
                if member != user_profile:  # Don't add the owner as a member
                    project.members.add(member)
                    messages.success(request, f"{member.user.username} added to project!")
                else:
                    messages.error(request, "You are already the owner of this project.")
            except UserProfile.DoesNotExist:
                messages.error(request, f"No user found with email {email}")
        
        elif action == 'remove' and member_id:
            try:
                member = UserProfile.objects.get(id=member_id)
                project.members.remove(member)
                messages.success(request, f"{member.user.username} removed from project!")
            except UserProfile.DoesNotExist:
                messages.error(request, "Member not found.")
    
    # Get current members
    members = project.members.all()
    
    context = {
        'project': project,
        'members': members,
        'active_page': 'projects'
    }
    
    return render(request, 'projects/project_members.html', context)

@login_required
@require_http_methods(["POST"])
def project_toggle_complete(request, project_id):
    """AJAX endpoint to toggle project completion status"""
    try:
        user_profile = request.user.userprofile
    except:
        return JsonResponse({'success': False, 'message': 'Please complete your profile first'})
    
    try:
        project = Project.objects.get(
            Q(id=project_id),
            Q(user=user_profile) | Q(members=user_profile)
        )
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Project not found or you do not have permission'
        })
    
    # Toggle completion status
    project.completed = not project.completed
    project.save()
    
    return JsonResponse({
        'success': True,
        'completed': project.completed,
        'message': f'Project marked as {"completed" if project.completed else "active"}'
    })
