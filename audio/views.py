import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse
import av


def merge_video_audio(video_path, audio_path, output_path):
    video_input = av.open(video_path)
    audio_input = av.open(audio_path)
    output = av.open(output_path, mode="w")

    # Add video stream (re-encoded to H264)
    video_stream = output.add_stream("h264", rate=video_input.streams.video[0].average_rate)
    video_stream.width = video_input.streams.video[0].codec_context.width
    video_stream.height = video_input.streams.video[0].codec_context.height
    video_stream.pix_fmt = "yuv420p"

    # Add audio stream (re-encoded to AAC)
    audio_stream = output.add_stream("aac", rate=audio_input.streams.audio[0].rate)

    # Encode video frames
    for frame in video_input.decode(video_input.streams.video[0]):
        packet = video_stream.encode(frame)
        if packet:
            output.mux(packet)

    # Encode audio frames
    for frame in audio_input.decode(audio_input.streams.audio[0]):
        packet = audio_stream.encode(frame)
        if packet:
            output.mux(packet)

    # Flush encoders
    for packet in video_stream.encode():
        output.mux(packet)
    for packet in audio_stream.encode():
        output.mux(packet)

    output.close()


def modify_video_with_audio(request):
    if request.method == "POST":
        video_file = request.FILES.get("video")
        audio_file = request.FILES.get("audio")

        if not video_file or not audio_file:
            return HttpResponse("Please upload both video and audio files.", status=400)

        # Temporary directory for saving files
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, video_file.name)
        audio_path = os.path.join(temp_dir, audio_file.name)
        output_path = os.path.join(temp_dir, "merged_output.mp4")

        # Save uploaded video
        with open(video_path, "wb+") as f:
            for chunk in video_file.chunks():
                f.write(chunk)

        # Save uploaded audio
        with open(audio_path, "wb+") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Merge video + audio
        merge_video_audio(video_path, audio_path, output_path)

        # Return merged file as response
        with open(output_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="video/mp4")
            response["Content-Disposition"] = 'attachment; filename="merged_video.mp4"'
            return response

    return render(request, "modify_video.html")
