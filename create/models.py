from django.db import models

from django.contrib.auth.models import User

class ProcessedVideo(models.Model):
    title = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the user
    video_path = models.FileField(upload_to='processed_videos/')  # Path to the processed video
    created_at = models.DateTimeField(auto_now_add=True)  # Time the video was processed

    def __str__(self):
        return f"{self.user.username} - {self.video_path}"



class BackgroundVideo(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='background_videos/')
    preview = models.FileField(upload_to='background_videos/previews/', null=True, blank=True)

    def __str__(self):
        return self.title


class FontsChoose(models.Model):
    title = models.CharField(max_length=100)
    font = models.FileField(upload_to='fonts/')

    def __str__(self):
        return self.title

class VoiceChoose(models.Model):
    title = models.CharField(max_length=100)
    api_id = models.CharField(max_length=100)
    voice = models.FileField(upload_to='voice_models/')
    
    def __str__(self):
        return self.title