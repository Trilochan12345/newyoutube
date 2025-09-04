from django.shortcuts import render, redirect
from django.contrib import messages
from .utils.youtube_upload import upload_to_youtube_scheduled
from Thumbnails.models import Thumbnail
from .models import YouTubeVideoUpload
import os, tempfile, logging

logger = logging.getLogger(__name__)

def publish_to_youtube_view(request):
    thumbnails = Thumbnail.objects.all().order_by('-created_at')

    if request.method == "POST":
        uploaded_file = request.FILES.get("video_file")
        uploaded_thumbnail = request.FILES.get("thumbnail_file")  # ✅ now defined
        selected_thumbnail_path = request.POST.get("thumbnail_path")  # ✅ separate var

        video_path = None
        thumbnail_path = None  # this will be determined later

        # --- Handle video file upload ---
        if uploaded_file:
            tmp_dir = tempfile.gettempdir()
            video_file_path = os.path.join(tmp_dir, uploaded_file.name)
            with open(video_file_path, 'wb+') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)
            video_path = video_file_path
        else:
            messages.error(request, "❌ Please upload a video file.")
            return redirect("publish_to_youtube")

        # --- Handle thumbnail upload (optional) ---
        if uploaded_thumbnail:
            tmp_dir = tempfile.gettempdir()
            thumb_file_path = os.path.join(tmp_dir, uploaded_thumbnail.name)
            with open(thumb_file_path, 'wb+') as dest:
                for chunk in uploaded_thumbnail.chunks():
                    dest.write(chunk)
            thumbnail_path = thumb_file_path
        elif selected_thumbnail_path:
            thumbnail_path = selected_thumbnail_path

        # --- Extract metadata ---
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        tags = [tag.strip() for tag in request.POST.get("tags", "AI,Python").split(",")]

        if not video_path or not title or not description:
            messages.error(request, "❌ Missing required fields.")
            return redirect("publish_to_youtube")

        if not os.path.isfile(video_path):
            messages.error(request, "❌ Video file not found on server.")
            return redirect("publish_to_youtube")

        try:
            video_id = upload_to_youtube_scheduled(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        thumbnail_path=thumbnail_path,
        
    )

            YouTubeVideoUpload.objects.create(
                title=title,
                description=description,
                tags=",".join(tags),
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                youtube_video_id=video_id,
                uploaded=True
            )

            messages.success(request, f"✅ Video uploaded! Video ID: {video_id}")
            return redirect("publish_to_youtube")

        except Exception as e:
            logger.exception("Upload failed")
            messages.error(request, f"❌ Upload failed: {str(e)}")
            return redirect("publish_to_youtube")

    return render(request, "youtube_upload.html", {"thumbnails": thumbnails})



def modify_view(request):
    
    return render(request, 'modify.html')