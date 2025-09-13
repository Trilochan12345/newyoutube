# image3d/models.py
from django.db import models

class GenerationRequest(models.Model):
    prompt = models.TextField()
    negative_prompt = models.TextField(blank=True, default="")
    num_images = models.PositiveSmallIntegerField(default=1)
    guidance = models.FloatField(default=7.5)
    steps = models.PositiveSmallIntegerField(default=28)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gen {self.id} - {self.created_at.isoformat()}"

class GeneratedImage(models.Model):
    request = models.ForeignKey(GenerationRequest, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="figurines/")
    seed = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
