from django.contrib import admin
from .models import BackgroundVideo, FontsChoose, VoiceChoose, ProcessedVideo

@admin.register(BackgroundVideo)
class BackgroundVideoAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(FontsChoose)
class FontsChooseAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(VoiceChoose)
class VoiceChooseAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(ProcessedVideo)
class ProcessedVideoAdmin(admin.ModelAdmin):
    list_display = ('video_path',)