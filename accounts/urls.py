from django.urls import path
from django.http import HttpResponse
from . import views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

def home_view(request):
    return render(request,'accounts/homepage.html')

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', home_view, name='home'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
