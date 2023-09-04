"""smart_table URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login, name='login'),
    path('landing/', views.landing, name='landing'),
    path('presence_list/', views.presence_list, name='presence_list'),
    path('github/', views.display_github_repository, name='git_files'),
    path('file/<str:file_name>/', views.display_github_file, name='display_github_file'),
    path('file/<str:subdirectory>/<str:file_name>/', views.display_github_file, name='display_github_file'),
    path('subdirectory/<str:subdirectory>/', views.display_github_subdirectory, name='display_github_subdirectory')
]
