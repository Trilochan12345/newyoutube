from django.db import models

# Create your models here.
class Thumbnail(models.Model):
    title = models.CharField(max_length=255)
    background = models.ImageField(upload_to='thumbnails/backgrounds/', blank=True, null=True)
    logo = models.ImageField(upload_to='thumbnails/logos/', blank=True, null=True)
    output = models.ImageField(upload_to='thumbnails/generated/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title