# tts/utils.py
import os
import hashlib
from pathlib import Path
from django.conf import settings
from gtts import gTTS
from pydub import AudioSegment, effects
import openai

# Cache directory for TTS
TTS_CACHE_DIR = Path(settings.MEDIA_ROOT) / "tts"
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def text_to_filename(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest() + ".mp3"

def normalize_audio(path: Path, target_dBFS: float = -20.0):
    audio = AudioSegment.from_file(path)
    change_in_dBFS = target_dBFS - audio.dBFS
    normalized = audio.apply_gain(change_in_dBFS)
    normalized = normalized.fade_in(200).fade_out(200)  # smooth start/end
    normalized.export(path, format="mp3")

def generate_tts(text: str, gender: str = "male") -> str:
    """Generate TTS with specified gender using OpenAI preferred, fallback gTTS"""
    file_path = TTS_CACHE_DIR / text_to_filename(text)

    if not file_path.exists():
        # Map gender to OpenAI voices
        voice_map = {
            "male": "alloy",
            "female": "aria"
        }
        selected_voice = voice_map.get(gender.lower(), "alloy")

        try:
            # OpenAI TTS
            response = openai.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=selected_voice,
                input=text
            )
            with open(file_path, "wb") as f:
                f.write(response.audio)
        except Exception as e:
            print(f"OpenAI TTS failed: {e}, falling back to gTTS")
            tts = gTTS(text, lang="en", slow=False)
            tts.save(file_path)

        normalize_audio(file_path)

    return str(file_path)
