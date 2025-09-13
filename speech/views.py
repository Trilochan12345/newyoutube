# tts/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import generate_tts
import json
import os
from django.conf import settings

@csrf_exempt
def tts_api(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        text = data.get('text')
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        # Generate TTS (male/female selectable)
        gender = data.get('gender', 'male')  # default male
        file_path = generate_tts(text, gender=gender)
        filename = os.path.basename(file_path)

        audio_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, 'tts', filename))
        return JsonResponse({'audio_url': audio_url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def tts_form_view(request):
    return render(request, "tts_form.html")
