from django.urls import path
from . import views

urlpatterns = [
     path('', views.player_page, name='player'),
    path('upload/', views.upload_song, name='upload'),
    path('stream/<int:song_id>/', views.stream_song, name='stream'),
    path('songs/', views.get_songs, name='song-list'),
    path('delete/<int:song_id>/', views.delete_song, name='delete_song'),
    path('rename/<int:song_id>/', views.rename_song, name='rename_song'),
]
