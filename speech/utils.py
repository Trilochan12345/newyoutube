# tts/utils.py
import os
import hashlib
from gtts import gTTS
from pydub import AudioSegment, effects
from django.conf import settings

TTS_CACHE_DIR = os.path.join(settings.MEDIA_ROOT, 'tts')
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

def text_to_filename(text):
    return hashlib.md5(text.encode()).hexdigest() + ".mp3"

def normalize_audio(path):
    audio = AudioSegment.from_file(path)
    normalized = effects.normalize(audio)
    normalized.export(path, format="mp3")

def generate_tts(text):
    filename = text_to_filename(text)
    file_path = os.path.join(TTS_CACHE_DIR, filename)
    
    if not os.path.exists(file_path):
        tts = gTTS(text)
        tts.save(file_path)
        normalize_audio(file_path)

    return file_path, filename
