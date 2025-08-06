from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from .models import Song
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.files.base import ContentFile
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io
from datetime import datetime,timedelta

def player_page(request):
    return render(request, 'musicplayer/he.html')

def format_duration(duration):
    if duration is None:
        return None
    total_seconds = int(duration.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{str(seconds).zfill(2)}"

def get_songs(request):
    songs = Song.objects.all().order_by('-date_added')
    return JsonResponse([
        {
            'id': song.id,
            'title': song.title,
            'album': song.album,
            'web_album':song.web_album,
            'date_added': song.date_added.isoformat(),
            'cover_url': song.cover.url if song.cover else None ,
            'duration' : format_duration(song.duration)
        }
        for song in songs
    ], safe=False)

@csrf_exempt
def upload_song(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        if not file.content_type.startswith('audio/'):
            return JsonResponse({'status': 'error', 'message': 'Invalid file type'}, status=400)

        if file.size > 50 * 1024 * 1024:
            return JsonResponse({'status': 'error', 'message': 'File too large'}, status=400)

        # Read data
        file_data = file.read()
        web_album_album = request.POST.get('web_album')
        # Save audio blob to DB
        song = Song.objects.create(
            title=file.name,
            content_type=file.content_type,
            data=file_data
        )

        try:
            audio = MP3(io.BytesIO(file_data), ID3=ID3)
            length_seconds = int(audio.info.length)
            duration_td = timedelta(seconds=length_seconds)
            song.duration = duration_td
            song.web_album=web_album_album
            song.save()


            album_tag = audio.get("TALB")
            if album_tag:
                song.album = album_tag.text[0]
            for tag in audio.tags.values():
                if isinstance(tag, APIC):  
                    image_data = tag.data
                    image_ext = tag.mime.split('/')[-1]  
                    song.cover.save(
                        f"{song.id}_cover.{image_ext}",
                        ContentFile(image_data),
                        save=True
                    )
                    break
        except Exception as e:
            print(f"[!] No album art or extraction error: {e}")

        return JsonResponse({
            'status': 'success',
            'id': song.id,
            'title': song.title,
            'web_album': song.web_album,
            'cover_url': song.cover.url if song.cover else None,
            'album' : song.album,
            'duration': duration_td
        })

    return JsonResponse({'status': 'error', 'message': 'No file provided'}, status=400)

from django.http import HttpResponse
import os
import re

def stream_song(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
    except Song.DoesNotExist:
        return Http404("Song not found.")

    data = song.data
    file_size = len(data)

    range_header = request.headers.get('Range')
    if range_header:
        match = re.match(r'^bytes=(\d+)-(\d*)$', range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            if start >= file_size:
                return HttpResponse(status=416)  # Range Not Satisfiable

            chunk = data[start:end + 1]
            response = HttpResponse(chunk, status=206)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        else:
            return HttpResponse(status=416)
    else:
        response = HttpResponse(data, status=200)

    response['Content-Length'] = len(response.content)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Type'] = song.content_type or 'audio/mpeg'
    return response



# musicplayer/views.py
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Song
import json

@require_POST
@csrf_exempt
def delete_song(request, song_id):
    try:
        song=Song.objects.get(id=song_id)
        song.cover.delete(save=False)
        song.delete()
        return JsonResponse({'status': 'success'})
    except Song.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)

@require_POST
@csrf_exempt
def rename_song(request, song_id):
    try:
        song = Song.objects.get(id=song_id)

        try:
            data = json.loads(request.body)
            new_title = data.get('title')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        if new_title:
            song.title = new_title
            song.save()
            return JsonResponse({'status': 'success', 'title': new_title})
        else:
            return JsonResponse({'status': 'error', 'message': 'Title required'}, status=400)

    except Song.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
