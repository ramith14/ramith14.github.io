from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def say(request,username):
    username = request.user.username  # Fetch the logged-in user's username
    return render(request, 'myweb/hell.html',{'name':username})


def delete_user_view(request,username):
    username = request.user.username 
    user = User.objects.get(username=username)
    user.delete()
    return redirect('/login/')

