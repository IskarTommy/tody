from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, date
from tasks.models import Task
import json
import calendar


@login_required
def dashboard_view(request):
    """
    Main dashboard view with productivity analytics
    """
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Get today's date
    today = timezone.now().date()

    # Basic task statistics
    all_tasks = Task.objects.filter(user=user_profile)
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(completed=True).count()

    # Today's statistics
    completed_today = all_tasks.filter(
        completed=True,
        updated_at__date=today
    ).count()

    due_today = all_tasks.filter(
        due_date=today,
        completed=False
    ).count()

    # Completion rate
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = round((completed_tasks / total_tasks) * 100)

    # Recent tasks (last 10)
    recent_tasks = all_tasks.order_by('-created_at')[:10]

    # High priority tasks that are not completed
    high_priority_tasks = all_tasks.filter(
        priority='high',
        completed=False
    ).order_by('due_date')[:5]

    # Weekly completion data for mini chart
    weekly_data = []
    for i in range(6, -1, -1):  # Last 7 days
        date = today - timedelta(days=i)
        completed_count = all_tasks.filter(
            completed=True,
            updated_at__date=date
        ).count()
        weekly_data.append(completed_count)

    # Advanced chart data
    # Productivity heatmap data (last 30 days)
    import json
    heatmap_data = []
    max_daily_tasks = 0

    for i in range(29, -1, -1):  # Last 30 days
        date = today - timedelta(days=i)
        day_completed = all_tasks.filter(
            completed=True,
            updated_at__date=date
        ).count()

        # Keep real data only - no dummy data to avoid conflicts

        heatmap_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'value': day_completed
        })
        max_daily_tasks = max(max_daily_tasks, day_completed)

    # Convert to JSON string for template
    heatmap_json = json.dumps(heatmap_data)

    # Priority distribution for radar chart
    priority_stats = {
        'high': all_tasks.filter(priority='high').count(),
        'medium': all_tasks.filter(priority='medium').count(),
        'low': all_tasks.filter(priority='low').count(),
    }

    # Task velocity calculation (tasks completed per week average)
    weeks_back = 4
    velocity_data = []
    for week in range(weeks_back):
        week_start = today - timedelta(days=(week * 7) + 6)
        week_end = today - timedelta(days=week * 7)
        week_completed = all_tasks.filter(
            completed=True,
            updated_at__date__range=[week_start, week_end]
        ).count()
        velocity_data.append(week_completed)

    avg_velocity = sum(velocity_data) / len(velocity_data) if velocity_data else 0

    context = {
        'total_tasks': total_tasks,
        'completed_today': completed_today,
        'due_today': due_today,
        'completion_rate': completion_rate,
        'recent_tasks': recent_tasks,
        'high_priority_tasks': high_priority_tasks,
        'weekly_data': weekly_data,
        # Advanced chart data
        'heatmap_data': heatmap_data,
        'heatmap_json': heatmap_json,
        'max_daily_tasks': max_daily_tasks,
        'priority_stats': priority_stats,
        'velocity_data': velocity_data,
        'avg_velocity': round(avg_velocity, 1),
        'active_page': 'dashboard'
    }

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def analytics_view(request):
    """
    Detailed analytics view with advanced charts
    """
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Get real data for analytics charts
    all_tasks = Task.objects.filter(user=user_profile)
    today = timezone.now().date()

    # Completion trends (last 4 weeks)
    completion_trends = []
    for week in range(3, -1, -1):
        week_start = today - timedelta(days=(week * 7) + 6)
        week_end = today - timedelta(days=week * 7)
        week_completed = all_tasks.filter(
            completed=True,
            updated_at__date__range=[week_start, week_end]
        ).count()
        completion_trends.append(week_completed)

    # Priority distribution (real data)
    priority_stats = {
        'high': all_tasks.filter(priority='high').count(),
        'medium': all_tasks.filter(priority='medium').count(),
        'low': all_tasks.filter(priority='low').count(),
    }

    # Time distribution (tasks completed by day of week)
    time_distribution = []
    for day in range(7):  # Monday = 0, Sunday = 6
        day_completed = all_tasks.filter(
            completed=True,
            updated_at__week_day=day + 2  # Django week_day: Sunday=1, Monday=2
        ).count()
        time_distribution.append(day_completed)

    # Productivity scores (calculated from real data)
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(completed=True).count()
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Calculate productivity metrics
    focus_score = min(100, completion_rate + 10)  # Bonus for completion
    efficiency_score = min(100, (completed_tasks / max(1, total_tasks)) * 100)
    consistency_score = min(100, len([x for x in completion_trends if x > 0]) * 25)
    quality_score = min(100, all_tasks.filter(priority='high', completed=True).count() * 20)
    speed_score = min(100, sum(completion_trends) * 10)

    productivity_scores = [focus_score, efficiency_score, consistency_score, quality_score, speed_score]

    high_priority_count = all_tasks.filter(priority='high', completed=False).count()

    context = {
        'completion_rate': completion_rate,
        'high_priority_count': high_priority_count,
        # Real chart data
        'completion_trends': completion_trends,
        'priority_stats': priority_stats,
        'time_distribution': time_distribution,
        'productivity_scores': productivity_scores,
        'active_page': 'analytics'
    }

    return render(request, 'dashboard/analytics.html', context)


@login_required
def reports_view(request):
    """
    Reports generation and management view
    """
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Get data for reports
    today = timezone.now().date()
    all_tasks = Task.objects.filter(user=user_profile)

    # Weekly completion count
    week_start = today - timedelta(days=today.weekday())
    completed_this_week = all_tasks.filter(
        completed=True,
        updated_at__date__gte=week_start
    ).count()

    # Overall completion rate
    completion_rate = 0
    if all_tasks.count() > 0:
        completed = all_tasks.filter(completed=True).count()
        completion_rate = round((completed / all_tasks.count()) * 100)

    # High priority tasks
    high_priority_tasks = all_tasks.filter(priority='high', completed=False)

    context = {
        'today': today,
        'completed_this_week': completed_this_week,
        'completion_rate': completion_rate,
        'high_priority_tasks': high_priority_tasks,
        'active_page': 'reports'
    }

    return render(request, 'dashboard/reports.html', context)


@login_required
def calendar_view(request):
    """
    Calendar view showing tasks in a monthly calendar format
    """
    try:
        user_profile = request.user.userprofile
    except:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Get current date or requested month/year
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Create calendar for the month (Sunday first - US style)
    calendar.setfirstweekday(6)  # 6 = Sunday
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Get all tasks for the user in this month
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    tasks_in_month = Task.objects.filter(
        user=user_profile,
        due_date__range=[month_start, month_end]
    ).order_by('due_date', 'priority')

    # Group tasks by date
    tasks_by_date = {}
    for task in tasks_in_month:
        if task.due_date:
            day = task.due_date.day
            if day not in tasks_by_date:
                tasks_by_date[day] = []
            tasks_by_date[day].append(task)

    # Navigation dates
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Quick stats for the month
    total_tasks_month = tasks_in_month.count()
    completed_tasks_month = tasks_in_month.filter(completed=True).count()
    overdue_tasks = Task.objects.filter(
        user=user_profile,
        due_date__lt=today,
        completed=False
    ).count()

    context = {
        'calendar_weeks': cal,
        'month': month,
        'year': year,
        'month_name': month_name,
        'today': today,
        'tasks_by_date': tasks_by_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'total_tasks_month': total_tasks_month,
        'completed_tasks_month': completed_tasks_month,
        'overdue_tasks': overdue_tasks,
        'active_page': 'calendar'
    }

    return render(request, 'dashboard/calendar.html', context)
