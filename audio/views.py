import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from moviepy import *



def modify_video_with_audio(request):
    if request.method == "POST":
        video_file = request.FILES.get("video")
        audio_file = request.FILES.get("audio")

        if not video_file or not audio_file:
            return HttpResponse("❌ Please upload both video and audio files.")

        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        unique_id = get_random_string(8)

        video_path = os.path.join(temp_dir, f"video_{unique_id}.mp4")
        audio_path = os.path.join(temp_dir, f"audio_{unique_id}.mp3")
        output_path = os.path.join(temp_dir, f"merged_{unique_id}.mp4")

        video_clip = None
        audio_clip = None
        final_clip = None

        try:
            # Save uploaded video
            with open(video_path, 'wb+') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)

            # Save uploaded audio
            with open(audio_path, 'wb+') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)

            # Load and combine
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)

            # Replace video audio
            final_clip = video_clip.set_audio(audio_clip)

            # Export final merged video
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

            # Serve as download
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="merged_{unique_id}.mp4"'
                return response

        except Exception as e:
            return HttpResponse(f"❌ Error while merging: {str(e)}")

        finally:
            # Close all clips
            for clip in [video_clip, audio_clip, final_clip]:
                if clip:
                    try:
                        clip.close()
                    except:
                        pass

            # Clean up temp
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    return render(request, "modify_video.html")
