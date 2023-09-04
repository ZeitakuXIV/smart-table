import base64
from django.shortcuts import render
from datetime import datetime, time
from pytz import timezone
from .presence_models import Presence  # Adjust the import path as needed
from .models import CustomUser
import requests
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import CustomUser  # Import your custom user model
from .forms import LoginForm  # Import your login form
import bcrypt

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Use your custom login form
        if form.is_valid():
            nis = form.cleaned_data['nis']  # Get NIS from the form
            password = form.cleaned_data['password']  # Get password from the form
            user = authenticate(request, nis=nis, password=password)
            if user is not None:
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session.save()
                return redirect('landing')  # Redirect to the desired page after login
            else:
                # Authentication failed, display an error message
                form.add_error(None, "Invalid credentials. Please try again.")
    else:
        form = LoginForm()  # Use your custom login form

    return render(request, 'presence_app/login.html', {'form': form})

def landing(request):
    user = request.session['user_name'];
    return render(request, 'presence_app/landing.html', {'user': user})

def presence_list(request):
    jakarta_timezone = timezone('Asia/Jakarta')
    now_jakarta = datetime.now(jakarta_timezone)
    start_of_day_jakarta = now_jakarta.replace(hour=0, minute=0, second=0, microsecond=0)
    
    users = CustomUser.objects.all()
    presence_status = []

    for user in users:
        todays_data = Presence.objects.filter(
            user=user,
            time_in__range=(start_of_day_jakarta, now_jakarta)
        ).order_by('time_in', 'time_out')
        has_presence_today = todays_data.exists()

        if has_presence_today:
            first_time_in = todays_data.first().time_in
            last_time_out = todays_data.last().time_out
        else:
            first_time_in = None
            last_time_out = None
        
        presence_status.append({
            'user': user,
            'has_presence_today': has_presence_today,
            'time_in': first_time_in,
            'time_out': last_time_out,
        })

        print(f"User: {user.name}, Has Presence Today: {has_presence_today}")
    
    context = presence_status
    return render(request, 'presence_app/presence_list.html', {'presences': context})

def display_github_repository(request):
    GITHUB_PAT = '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'
    owner = "ichifour"
    repo_name = "smart-table"
    path = request.session['user_id']
    headers = {
        'Authorization': f'Bearer {GITHUB_PAT}',  # Include your PAT here
        'Accept': 'application/vnd.github+json'  # Specify the API version
    }

    # Fetch a list of files in the directory from GitHub
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo_name}/contents/{path}',
        headers=headers
    )

    if response.status_code == 200:
        files = response.json()
        context = {
            "files": files,
            "subdirectory": None
        }
        # Render the files in an ordered list
        return render(request, 'presence_app/git_files.html', {'context': context})
    else:
        error_message = f"Error fetching files: {response.status_code}"
        return render(request, 'presence_app/error.html', {'error_message': error_message})
    

def display_github_file(request, file_name, subdirectory = None):
    GITHUB_PAT = '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'
    owner = "ichifour"
    repo_name = "smart-table"
    if(subdirectory != None):
        path = f"{request.session['user_id']}/{subdirectory}/{file_name}"
    else:
        path = f"{request.session['user_id']}/{file_name}"
    headers = {
        'Authorization': f'Bearer {GITHUB_PAT}',  # Include your PAT here
        'Accept': 'application/vnd.github+json'  # Specify the API version
    }

    # Fetch a list of files in the directory from GitHub
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo_name}/contents/{path}',
        headers=headers
    )
    if response.status_code == 200:
        content = response.json().get('content')
        # Decode content from base64
        content = base64.b64decode(content).decode('utf-8')
        return render(request, 'presence_app/file_viewer.html', {'content': content})
    else:
        error_message = f"Error fetching file: {response.status_code}"
        return render(request, 'presence_app/error.html', {'error_message': error_message})

def display_github_subdirectory(request, subdirectory):
    GITHUB_PAT = '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'
    owner = "ichifour"
    repo_name = "smart-table"
    path = f"{request.session['user_id']}/{subdirectory}"  # Subdirectory path
    headers = {
        'Authorization': f'Bearer {GITHUB_PAT}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo_name}/contents/{path}',
        headers=headers
    )

    if response.status_code == 200:
        files = response.json()
        context = {
            "subdirectory": subdirectory,
            "files": files
        }
        return render(request, 'presence_app/git_files.html', {'context': context})
    else:
        error_message = f"Error fetching file: {response.status_code}"
        return render(request, 'presence_app/error.html', {'error_message': error_message})