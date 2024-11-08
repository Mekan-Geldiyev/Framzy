from django import forms
from .models import BackgroundVideo, FontsChoose, VoiceChoose
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # Set email as username
        if commit:
            user.save()
        return user


class SplitVideoForm(forms.Form):
    background_video = forms.ModelChoiceField(queryset=BackgroundVideo.objects.all(), required=True)
    bottom_video = forms.FileField(required=True)
    selected_font = forms.ModelChoiceField(queryset=FontsChoose.objects.all(), required=True)
    producer_tag = forms.CharField(required=False)
    filename = forms.CharField(required=True)
    POSITION_CHOICES = [
        ('top', 'Background video on top, Podcast/Celebrity clip on bottom'),
        ('bottom', 'Background video on bottom, Podcast/Celebrity clip on top'),
    ]
    CAPTIONS_CHOICES = [
        ('yes_captions', 'I want captions on my video.'),
        ('no_captions', 'I do NOT want captions on my video.'),
    ]
    position = forms.ChoiceField(choices=POSITION_CHOICES, required=True)
    captions = forms.ChoiceField(choices=CAPTIONS_CHOICES, required=True)

class ClipAnythingForm(forms.Form):
    video_to_analyze = forms.FileField(required=True)
    highlights = forms.CharField(required=True)
    selected_font = forms.ModelChoiceField(queryset=FontsChoose.objects.all(), required=True)

class OneVidForm(forms.Form):
    background_video = forms.ModelChoiceField(queryset=BackgroundVideo.objects.all(), required=True)
    producer_tag = forms.CharField(required=False)
    selected_font = forms.ModelChoiceField(queryset=FontsChoose.objects.all(), required=True)
    script = forms.CharField(required=False)
    filename = forms.CharField(required=True)
    voice = forms.ModelChoiceField(queryset=VoiceChoose.objects.all(), required=True)
    
class OneVidCustomForm(forms.Form):
    main_video = forms.FileField(required=True)
    producer_tag = forms.CharField(required=False)
    filename = forms.CharField(required=True)
    selected_font = forms.ModelChoiceField(queryset=FontsChoose.objects.all(), required=True)
    mainText = forms.CharField(required=False)

    SOUND_CHOICES = [
        ('yes', 'I want the original audio of the video.'),
        ('no', 'Mute the original audio so I can put music over it myself'),
    ]
    sound = forms.ChoiceField(choices=SOUND_CHOICES, required=True)
    SHAPE_CHOICES = [
        ('square', 'I want the clip to be cut into a square and in the middle of the screen'),
        ('full_screen', 'I want the entire screen to be covered with the video'),
    ]
    shape = forms.ChoiceField(choices=SHAPE_CHOICES, required=True)

    FADE_CHOICES = [
        ('fade', 'I want to fade in and out of my clip'),
        ('noFade', 'I do NOT want to fade in and out of my clip'),
    ]
    fade = forms.ChoiceField(choices=FADE_CHOICES, required=True)