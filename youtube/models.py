from django.db import models

class YouTubeVideoUpload(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=512, blank=True, help_text="Comma-separated tags")
    
    video_file = models.FileField(upload_to="youtube_uploads/videos/", blank=True, null=True)
    video_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path on server (if not uploading file)")

    thumbnail_path = models.CharField(max_length=500, blank=True, null=True)
    caption_path = models.CharField(max_length=500, blank=True, null=True)

    youtube_video_id = models.CharField(max_length=32, blank=True, null=True)
    uploaded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
