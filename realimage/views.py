import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from diffusers import StableDiffusionPipeline
import torch
import re
from django.http import FileResponse
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from urllib.parse import urlparse
from speech import views
import threading
from .utils.youtube_upload import upload_to_youtube_scheduled
from moviepy.audio.io.AudioFileClip import AudioFileClip
import soundfile as sf
# Load Stable Diffusion once
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
)
pipe = pipe.to(DEVICE)

MAX_PROMPT_LENGTH = 200  # max characters



@csrf_exempt
def generate_sd_image(request):
    """API endpoint: /generate-image/?prompt=..."""
    prompt = (request.POST.get("prompt") or request.GET.get("prompt") or "").strip()

    if not prompt:
        return JsonResponse({"error": "Missing prompt"}, status=400)

    if len(prompt) > MAX_PROMPT_LENGTH:
        return JsonResponse({"error": f"Prompt too long. Max {MAX_PROMPT_LENGTH} characters allowed."}, status=400)

    try:
        result = pipe(prompt)
        image = result.images[0]

        save_dir = os.path.join(settings.MEDIA_ROOT, "ai_images")
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        fullpath = os.path.join(save_dir, filename)
        image.save(fullpath)

        local_url = settings.MEDIA_URL + "ai_images/" + filename

        return JsonResponse({
            "prompt": prompt,
            "image_url": local_url
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)





def make_video_from_images(image_dir, output_path, fps=2):
    """
    Create a video from all images in image_dir.
    fps = frames per second (higher = faster slideshow).
    """
    # Get all images (sorted oldest → newest)
    images = sorted(
        [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".png")]
    )
    if not images:
        return None

    clip = ImageSequenceClip(images, fps=fps)
    clip.write_videofile(output_path, codec="libx264", audio=False)

    return output_path




@csrf_exempt


def split_prompt(text):
    """
    Split text into smaller prompts.
    - First by newlines
    - Then by full stops (periods only)
    """
    parts = []
    for line in text.split("\n"):
        for p in re.split(r'[.]', line):  # ✅ split only on periods
            if p.strip():
                parts.append(p.strip())
    return parts


def image_form(request):
    """HTML form endpoint: /image-form/"""
    context = {"entered_prompts": ""}
    all_images = []

    if request.method == "POST":
        entered_prompts = request.POST.get("prompts", "")
        context["entered_prompts"] = entered_prompts

        # ✅ Split input into multiple smaller prompts
        prompt_list = split_prompt(entered_prompts)

        for prompt in prompt_list:
            try:
                result = pipe(prompt)
                image = result.images[0]

                save_dir = os.path.join(settings.MEDIA_ROOT, "ai_images")
                os.makedirs(save_dir, exist_ok=True)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{prompt[:20].replace(' ', '_')}.png"
                fullpath = os.path.join(save_dir, filename)
                image.save(fullpath)

                all_images.append({
                    "url": settings.MEDIA_URL + "ai_images/" + filename,
                    "prompt": prompt
                })

            except Exception as e:
                context["error"] = str(e)

    # ✅ Always load all images (new + old) from disk
    images_dir = os.path.join(settings.MEDIA_ROOT, "ai_images")
    if os.path.exists(images_dir):
        for fname in sorted(os.listdir(images_dir), reverse=True):  # newest first
            if not any(img["url"].endswith(fname) for img in all_images):
                all_images.append({
                    "url": settings.MEDIA_URL + "ai_images/" + fname,
                    "prompt": fname.split("_", 1)[-1].replace(".png", "").replace("_", " ")
                })

    context["all_images"] = all_images
    return render(request, "generate_image.html", context)


# ✅ Keep defaults global
DEFAULT_PROMPTS = [
    "A beautiful sunset over the ocean",
    "A futuristic cyberpunk city at night",
    "A magical forest with glowing mushrooms"
]



@csrf_exempt
def generate_video(request):
    """Generate video from selected images and upload to YouTube automatically"""
    if request.method == "POST":
        selected = request.POST.getlist("selected_images")
        if not selected:
            return JsonResponse({"error": "No images selected"}, status=400)

        # Convert URLs back to file paths
        image_paths = []
        for url in selected:
            path = urlparse(url).path  # e.g., /media/ai_images/xxxx.png
            relative_path = path.replace(settings.MEDIA_URL, "", 1)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            if os.path.exists(full_path):
                image_paths.append(full_path)

        if not image_paths:
            return JsonResponse({"error": "No valid images found"}, status=400)

        # Create output directory
        video_dir = os.path.join(settings.MEDIA_ROOT, "ai_videos")
        os.makedirs(video_dir, exist_ok=True)

        filename = f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        video_path = os.path.join(video_dir, filename)

        # Generate video from images
        clip = ImageSequenceClip(image_paths, fps=1)  # adjust fps if needed

        # === Add background music ===
        music_path = os.path.join(settings.MEDIA_ROOT, "bg_music.mp3")  # change path
        if os.path.exists(music_path):
            audio = AudioFileClip(music_path).subclip(0, clip.duration)
            clip = clip.set_audio(audio)

        # Export video with audio
        clip.write_videofile(video_path, codec="libx264", audio_codec="aac")

        # --- Upload to YouTube in background ---
        title = f"AI Generated Video {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        description = "Video generated automatically from selected AI images."
        tags = ["AI", "Generated", "ImageToVideo"]

        threading.Thread(
            target=async_upload,
            args=(video_path, title, description, tags),
            daemon=True
        ).start()

        # Respond immediately
        video_url = settings.MEDIA_URL + "ai_videos/" + filename
        return JsonResponse({
            "message": "✅ Video generated successfully with music. Uploading to YouTube...",
            "local_video_url": video_url
        })

    return JsonResponse({"error": "Invalid request"}, status=405)

def async_upload(video_path, title, description, tags):
    """Run YouTube upload in a background thread"""
    try:
        video_url = upload_to_youtube_scheduled(video_path, title, description, tags, None)
        print("✅ Uploaded to YouTube:", video_url)
    except Exception as e:
        print("❌ YouTube upload failed:", e)



