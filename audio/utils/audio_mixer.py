import os
import random
from pydub import AudioSegment

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(BASE_DIR, '..', 'assets', 'music')
SFX_DIR = os.path.join(BASE_DIR, '..', 'assets', 'sfx')
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'media', 'output')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'mixed.wav')

# === UTILITIES ===

def get_random_music():
    files = [f for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".wav"))]
    if not files:
        raise FileNotFoundError("No background music found in assets/music/")
    chosen = random.choice(files)
    print(f"🎵 Selected music: {chosen}")
    return AudioSegment.from_file(os.path.join(MUSIC_DIR, chosen))

def get_sfx(name):
    sfx_path = os.path.join(SFX_DIR, f"{name}.mp3")
    if not os.path.exists(sfx_path):
        raise FileNotFoundError(f"SFX '{name}' not found.")
    return AudioSegment.from_file(sfx_path)

def duck_background_music(bg_music, voice, duck_db=-15):
    # Loop background if it's shorter than voice
    looped_music = bg_music * ((len(voice) // len(bg_music)) + 1)
    looped_music = looped_music[:len(voice)]
    ducked = looped_music - abs(duck_db)
    return ducked.overlay(voice)

def inject_sfx(audio, sfx_name, position_ms):
    sfx = get_sfx(sfx_name)
    return audio.overlay(sfx, position=position_ms)

# === MAIN FUNCTION ===

def mix_audio(voiceover_path):
    if not os.path.exists(voiceover_path):
        raise FileNotFoundError("Voiceover file not found.")

    voiceover = AudioSegment.from_file(voiceover_path)
    background_music = get_random_music()
    mixed_audio = duck_background_music(background_music, voiceover, duck_db=-15)

    # Optional SFX injection (example at 500ms and 2s)
    mixed_audio = inject_sfx(mixed_audio, "whoosh", position_ms=500)
    mixed_audio = inject_sfx(mixed_audio, "pop", position_ms=2000)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    mixed_audio.export(OUTPUT_PATH, format="wav")

    return OUTPUT_PATH
