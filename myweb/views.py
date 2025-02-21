from django.shortcuts import render
from django.http import HttpResponse



def say(request):
    x=1
    y=2
    return render(request,'myweb/hell.html',{ 'name' : 'Ramith'})