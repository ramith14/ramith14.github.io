from django.urls import path
from . import views


urlpatterns=[
    path('cool/<str:username>',views.say,name="home"),
path('cool/delete/<str:username>', views.delete_user_view, name='deletionofuser')]