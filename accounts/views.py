# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import UserProfile



def test_page_view(request):
    return HttpResponse("<h1>Accounts URL is working!</h1>")

def login_view(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    context = {}
    if request.method == 'POST':
        # --- CHANGE 1: Capture POST data for re-rendering form on error ---
        context['form_data'] = request.POST

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password')
            # --- CHANGE 2: Pass context back to the template ---
            return render(request, 'accounts/login.html', context)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Set session expiry based on remember_me
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                # Redirect to next page or dashboard
                next_url = request.GET.get('next', 'accounts:profile')
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account has been deactivated')
        else:
            messages.error(request, 'Invalid username or password')
    
    # --- CHANGE 3: Pass context on POST failure or GET request ---
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return redirect('accounts:login')

def signup_view(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    context = {}
    if request.method == 'POST':
        # --- CHANGE 4: Capture POST data for re-rendering form on error ---
        context['form_data'] = request.POST

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        # The template uses 'password' and 'password2'. We'll stick to that.
        password = request.POST.get('password', '') 
        password2 = request.POST.get('password2', '')
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists')
        
        if not email:
            errors.append('Email is required')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already exists')
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if password != password2:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            # --- CHANGE 5: Add a return statement to show errors immediately ---
            return render(request, 'accounts/signup.html', context)
        else:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password, # Use the correct password variable
                    first_name=first_name,
                    last_name=last_name
                )
                
                # UserProfile is automatically created by signals
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('accounts:login')
                
            except Exception as e:
                messages.error(request, 'An error occurred while creating your account. Please try again.')
    
    # --- CHANGE 6: Pass context on POST failure or GET request ---
    return render(request, 'accounts/signup.html', context)

@login_required
def profile_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    # --- CHANGE 7: Pass back POST data on form submission for re-population ---
    context = {'profile': profile}
    if request.method == 'POST':
        context['form_data'] = request.POST

        # Update user info
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        
        # Update profile info
        profile.bio = request.POST.get('bio', '').strip()
        profile.phone = request.POST.get('phone', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.theme_preference = request.POST.get('theme_preference', 'light')
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html', context)

@login_required
@require_http_methods(["POST"])
def change_password_view(request):
    current_password = request.POST.get('current_password', '')
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    
    if not request.user.check_password(current_password):
        messages.error(request, 'Current password is incorrect')
    elif len(new_password1) < 8:
        messages.error(request, 'New password must be at least 8 characters long')
    elif new_password1 != new_password2:
        messages.error(request, 'New passwords do not match')
    else:
        request.user.set_password(new_password1)
        request.user.save()
        # Log the user out and require them to log in again with the new password
        logout(request)
        messages.success(request, 'Password changed successfully! Please log in again.')
        return redirect('accounts:login') 
    
    return redirect('accounts:profile')

# AJAX view for checking username availability
def check_username(request):
    username = request.GET.get('username', '').strip()
    is_available = not User.objects.filter(username=username).exists() if username else False
    return JsonResponse({'available': is_available})