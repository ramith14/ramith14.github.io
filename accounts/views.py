from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from .models import CustomUser
from .forms import CustomUserCreationForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    error = ''
    if request.method == 'POST':
        identifier = request.POST.get('username')  # This can be username or email
        password = request.POST.get('password')

        user = None
        # Try to find user by username or email
        try:
            # First try username
            user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            try:
                # If not found by username, try email
                user = CustomUser.objects.get(email=identifier)
            except CustomUser.DoesNotExist:
                user = None

        if user:
            if not user.check_password(password):
                error = 'Invalid password'
            else:
                login(request, user)
                # Use f-string correctly with redirect
                return redirect(f'/myweb/cool/{user.username}')
        else:
            error = 'Invalid username or email'

        # Optionally also check with AuthenticationForm (not strictly needed)
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(f'/myweb/cool/{user.username}')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')
