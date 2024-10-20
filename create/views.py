from django.shortcuts import render
from moviepy.editor import CompositeVideoClip, ColorClip, TextClip, ImageClip, VideoFileClip, CompositeVideoClip, AudioFileClip
import os
import tempfile
import shutil
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import threading
from django.http import HttpResponse, HttpResponseServerError
import io
from .models import BackgroundVideo
from .forms import SplitVideoForm, OneVidForm, OneVidCustomForm, ClipAnythingForm
import assemblyai as aai
from .models import FontsChoose, BackgroundVideo, VoiceChoose, ProcessedVideo
import requests
from PIL import Image, ImageFilter
import sieve
from moviepy.video.fx.all import resize
from moviepy.config import change_settings

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the user's videos page after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'registration/login.html')
@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


#AUTHENTICATION
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('login')  # Redirect to homepage or profile page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


#CREATED VIDEOS VIEWING
@login_required
def my_videos(request):
    # Query all processed videos for the logged-in user
    user_videos = ProcessedVideo.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_videos.html', {'videos': user_videos})










#VIDEO CREATION
imagemagick_path = "C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
#change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
#no clue man

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

def homePage(request):
    userName = request.user
    return render(request, 'home.html', {'userName': userName})


aai.settings.api_key = "02fdbdf25a5441b8ac2ebcccf6961f85"
CHATGPT_API_KEY = "sk-proj-niwWVgGiQhPzfqRZCeb8T3BlbkFJTWiMo2npk9KFUhjeHLXA"
# Create your views here.
def crop_center(clip, target_width, target_height):
    video_aspect_ratio = clip.size[0] / clip.size[1]
    target_aspect_ratio = target_width / target_height

    if video_aspect_ratio > target_aspect_ratio:
        new_width = int(target_aspect_ratio * clip.size[1])
        new_height = clip.size[1]
    else:
        new_width = clip.size[0]
        new_height = int(clip.size[0] / target_aspect_ratio)

    center_x, center_y = clip.size[0] // 2, clip.size[1] // 2
    left = center_x - new_width // 2
    right = center_x + new_width // 2
    top = center_y - new_height // 2
    bottom = center_y + new_height // 2

    return clip.crop(x1=left, y1=top, x2=right, y2=bottom).resize(newsize=(target_width, target_height))

def transcribe_audio_with_assemblyai(audio_path):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path)
    
    # Check if transcription was successful
    if transcript.status == aai.TranscriptStatus.error:
        raise ValueError(f"Transcription failed: {transcript.error}")
    
    return transcript.words  # Returns word-level timings

def create_caption_clips(cropped_video, transcription_words, font_path, target_height):
    # Start making the caption clips
    caption_clips = []
    
    # Loop over the transcription words to create TextClip for each word
    for word_obj in transcription_words:
        word = word_obj.text
        start_time = word_obj.start / 1000  # Convert milliseconds to seconds
        end_time = word_obj.end / 1000  # Convert milliseconds to seconds
        
        # Create TextClip for each word
        txt_clip = TextClip(word, fontsize=70, color='white', font=font_path)
        txt_clip = txt_clip.set_position(('center', target_height-100)).set_duration(end_time - start_time)
        txt_clip = txt_clip.set_start(start_time)
        
        caption_clips.append(txt_clip)
    
    # Combine the cropped video with the caption clips
    final_video = CompositeVideoClip([cropped_video] + caption_clips)
    return final_video


def create_split_video(request):
    processed_videos = []
    if request.method == 'POST':
        form = SplitVideoForm(request.POST, request.FILES)
        if form.is_valid():
            background_video = form.cleaned_data['background_video'].video.path
            bottom_video = request.FILES['bottom_video']
            selected_font_id = form.cleaned_data['selected_font'].id
            producer_tag = form.cleaned_data['producer_tag']
            filename = form.cleaned_data['filename']
            position = form.cleaned_data['position']
            captions = form.cleaned_data['captions']

            selected_font = FontsChoose.objects.get(id=selected_font_id)

            # Function to transcribe audio using AssemblyAI
            def transcribe_audio(audio_path):
                transcriber = aai.Transcriber()
                return transcriber.transcribe(audio_path)

            # Phone resolution (width, height)
            phone_resolution = (1080, 1920)
            target_height = phone_resolution[1] // 2
            #soon this font will also be able to be chosen by the user
            font_path = selected_font.font.path
            # Load top and bottom clips
            top_clip = VideoFileClip(background_video)
            bottom_clip = VideoFileClip(bottom_video.temporary_file_path())

            # Resize clips
            top_clip_resized = top_clip.resize(height=target_height).set_duration(bottom_clip.duration)
            bottom_clip_resized = bottom_clip.resize(height=target_height)

            # Position clips based on user choice
            if position == 'top':
                top_clip_positioned = top_clip_resized.set_position(("center", 0))
                bottom_clip_positioned = bottom_clip_resized.set_position(("center", target_height))
            else:
                top_clip_positioned = top_clip_resized.set_position(("center", target_height))
                bottom_clip_positioned = bottom_clip_resized.set_position(("center", 0))

            username_clip = TextClip(f"{producer_tag}", fontsize=40, color='white', font=font_path).set_position(('center', phone_resolution[1] - 200))

            # Set the duration of the username clip to match the final composition
            username_clip = username_clip.set_duration(bottom_clip.duration)
            # Composite final video clip
            final_clip = CompositeVideoClip([top_clip_positioned, bottom_clip_positioned, username_clip], size=phone_resolution)

            # Transcribe audio of the bottom video
            if captions == "yes_captions":
                try:
                    #transcription = transcribe_audio(bottom_video.temporary_file_path())
                    transcription_words = transcribe_audio_with_assemblyai(bottom_video.temporary_file_path())
                    print(transcription_words)
                    

                    # Split transcription into segments
                    final_clip = create_caption_clips(final_clip, transcription_words, font_path, target_height)

                except Exception as e:
                    transcription_text = f"Transcription error: {str(e)}"
                    print(transcription_text)  # Debugging output
                    # Handle transcription error

            # Save the final video
            #video_path = f"media/processed_videos/{request.user}_{filename}.mp4"
            #final_clip.write_videofile(video_path, codec='libx264', fps=30)


            output_dir = os.path.join("media", "processed_videos")
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{request.user}-{filename}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            relative_video_path = f"processed_videos/{output_filename}"
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

            ProcessedVideo.objects.create(title=filename, user=request.user, video_path=relative_video_path)
            # Read the video file
            processed_videos.append(f"/media/processed_videos/{output_filename}")
            

            # Create an HTTP response with the video data
            return render(request, 'create_split_video.html', {'videos': processed_videos})

    else:
        form = SplitVideoForm()

    fonts = FontsChoose.objects.all()
    background_videos = BackgroundVideo.objects.all()
    return render(request, 'create_split_video.html', {'form': form, 'fonts': fonts, 'background_videos': background_videos})

CHUNK_SIZE = 1024



@login_required
def clipAnything(request):
    phone_resolution = (1080, 1920)
    target_height = phone_resolution[1] // 2
    processed_videos = []

    if request.method == 'POST':
        form = ClipAnythingForm(request.POST, request.FILES)
        if form.is_valid():
            videoAnalyze = request.FILES['video_to_analyze']
            selected_font_id = form.cleaned_data['selected_font'].id
            selected_font = FontsChoose.objects.get(id=selected_font_id)
            font_path = selected_font.font.path

            # Save uploaded video to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in videoAnalyze.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            try:
                # Run Sieve function to generate highlights
                file = sieve.File(tmp_file_path)
                render_clips = True
                highlight_search_phrases = form.cleaned_data['highlights']
                highlights = sieve.function.get("sieve/highlights")
                output = highlights.run(file, render_clips, highlight_search_phrases)

                # Create output directory if it doesn't exist
                output_dir = os.path.join("media", "processed_videos")
                os.makedirs(output_dir, exist_ok=True)
                
                # Process all highlight videos returned by Sieve
                for idx, (file_obj, metadata) in enumerate(output):
                    if hasattr(file_obj, 'path'):
                        remote_path = file_obj.path  # Retrieve the remote file path

                        # Load and crop the video
                        clip = VideoFileClip(remote_path)
                        cropped_clip = crop_center(clip, phone_resolution[0], phone_resolution[1])

                        # Transcribe the audio using AssemblyAI and get the word timings
                        transcription_words = transcribe_audio_with_assemblyai(remote_path)

                        # Create the caption clips synchronized with the transcription
                        final_clip = create_caption_clips(cropped_clip, transcription_words, font_path, target_height)

                        # Save each processed video to the output directory
                        output_filename = f"{request.user}-{metadata['title']}_highlight_{idx}.mp4"
                        output_path = os.path.join(output_dir, output_filename)
                        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

                        # Append the processed video path to the list for rendering later
                        processed_videos.append(f"/media/processed_videos/{output_filename}")
                        relative_video_path = f"processed_videos/{output_filename}"
                        # Save to the database so the user can access it later
                        ProcessedVideo.objects.create(title=metadata['title'], user=request.user, video_path=relative_video_path)

                        print(f"Saved cropped and captioned clip to: {output_path}")
                    else:
                        print(f"No downloadable file for clip {idx}")

            finally:
                # Clean up the temporary file after all processing is complete
                os.remove(tmp_file_path)

            # After processing all videos, render them on a results page
            return render(request, 'clipAnything.html', {'videos': processed_videos})

        else:
            print("Invalid form submission")
    else:
        form = ClipAnythingForm()

    fonts = FontsChoose.objects.all()

    return render(request, 'clipAnything.html', {'form': form, 'fonts': fonts})

def create_oneVid(request):
    if request.method == 'POST':
        form = OneVidForm(request.POST, request.FILES)
        if form.is_valid():
            background_video = form.cleaned_data['background_video'].video.path
            producer_tag = form.cleaned_data['producer_tag']
            selected_font_id = form.cleaned_data['selected_font'].id
            selected_font = FontsChoose.objects.get(id=selected_font_id)
            font_path = selected_font.font.path
            script = form.cleaned_data['script']
            selected_voice = form.cleaned_data['voice']
            filename = form.cleaned_data['filename']
            voice_api_id = selected_voice.api_id

            phone_resolution = (1080, 1920)  # width, height (portrait orientation)
            clip = VideoFileClip(background_video)

            cropped_clip = crop_center(clip, phone_resolution[0], phone_resolution[1])

            if len(script) > 50:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_api_id}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": "sk_29cbe6ce5633c58426119d66fe1bcffefbe76f8522912bd8"
                }
                data = {
                    "text": script,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
                response = requests.post(url, json=data, headers=headers)
                audio_path = 'output.mp3'
                with open(audio_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                
                audio_clip = AudioFileClip(audio_path)
                audio_duration = audio_clip.duration

                cropped_clip = cropped_clip.set_duration(audio_duration)
                final_clip = CompositeVideoClip([cropped_clip], size=phone_resolution).set_duration(audio_duration).set_audio(audio_clip)

                username_clip = TextClip(f"{producer_tag}", fontsize=40, color='white', font=font_path).set_position(('center', phone_resolution[1] - 200)).set_duration(audio_duration)
                final_clip = CompositeVideoClip([final_clip, username_clip])

                words = script.split()
                segmented_texts = [' '.join(words[i:i + 3]) for i in range(0, len(words), 3)]
                caption_duration = audio_duration / len(segmented_texts)
                phone_resolution = (1080, 1920)
                target_height = phone_resolution[1] // 2
                caption_clips = []
                for idx, text in enumerate(segmented_texts):
                    start_time = idx * caption_duration
                    end_time = min((idx + 1) * caption_duration, audio_duration)
                    caption_clip = TextClip(text, fontsize=70, color='white', stroke_color='black', font=font_path, stroke_width=2, size=(phone_resolution[0], 150), method='caption')
                    caption_clip = caption_clip.set_start(start_time).set_end(end_time).set_position(('center', target_height-100))
                    caption_clips.append(caption_clip)

                final_clip = CompositeVideoClip([final_clip] + caption_clips)
            else:
                cropped_clip = cropped_clip.set_duration(clip.duration)
                final_clip = CompositeVideoClip([cropped_clip], size=phone_resolution)
                username_clip = TextClip(f"{producer_tag}", fontsize=40, color='white', font=font_path).set_position(('center', phone_resolution[1] - 200)).set_duration(clip.duration)
                final_clip = CompositeVideoClip([final_clip, username_clip])


            
            output_dir = os.path.join("media", "processed_videos")
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{request.user}-{filename}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            relative_video_path = f"processed_videos/{output_filename}"
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

            ProcessedVideo.objects.create(title=filename, user=request.user, video_path=relative_video_path)
            # Read the video file
            processed_videos = [(f"/media/processed_videos/{output_filename}")]


            return render(request, 'create_oneVid.html', {'videos': processed_videos})

    else:
        form = OneVidForm()

    fonts = FontsChoose.objects.all()
    voices = VoiceChoose.objects.all()
    background_videos = BackgroundVideo.objects.all()
    return render(request, 'create_oneVid.html', {'form': form, 'fonts': fonts, 'voices': voices, 'background_videos': background_videos})



def create_oneVidCustom(request):
    if request.method == 'POST':
        form = OneVidCustomForm(request.POST, request.FILES)
        if form.is_valid():
            mainVideo = request.FILES['main_video']
            producer_tag = form.cleaned_data['producer_tag']
            selected_font_id = form.cleaned_data['selected_font'].id
            selected_font = FontsChoose.objects.get(id=selected_font_id)
            font_path = selected_font.font.path
            mainText = form.cleaned_data['mainText']
            sound = form.cleaned_data['sound']
            shape = form.cleaned_data['shape']
            fade = form.cleaned_data['fade']
            if(sound == "yes"):
                clip = VideoFileClip(mainVideo.temporary_file_path())
            elif(sound == "no"):
                clip = VideoFileClip(mainVideo.temporary_file_path(), audio=False)
                
            display_duration = clip.duration
            phone_resolution = (1080, 1920)
            fade_duration = 1

            def wrap_text(text, width=33):
                words = text.split()
                lines = []
                line = ''
                for word in words:
                    if len(line + ' ' + word) <= width:
                        line += ' ' + word
                    else:
                        lines.append(line.strip())
                        line = word
                lines.append(line.strip())
                return '\n'.join(lines)

            # Wrap the text
            wrapped_text = wrap_text(mainText)
            # Create a text clip
            background_clip = ColorClip(size=phone_resolution, color=(0, 0, 0)).set_duration(display_duration + 2 * fade_duration)
            text_clip = TextClip(wrapped_text, fontsize=60, color='white', font=font_path, stroke_color='black', stroke_width=2, align='center').set_duration(display_duration).set_position(("center", phone_resolution[1] * 0.1))
            
            username_clip = TextClip(f"{producer_tag}", fontsize=40, color='white', font=font_path).set_position(('center', phone_resolution[1] - 200)).set_duration(clip.duration)
            target_height = phone_resolution[1] // 2

            if(shape == "full_screen"):
                cropped_clip = crop_center(clip, phone_resolution[0], phone_resolution[1])
            elif(shape == "square"):
                cropped_clip = clip.resize(height=target_height).set_position(("center", phone_resolution[1] * 0.3))

            if(fade == "fade"):
                final_clip = CompositeVideoClip([cropped_clip, username_clip, text_clip], size=phone_resolution).fadein(fade_duration).fadeout(fade_duration)
            elif(fade == "noFade"):
                final_clip = CompositeVideoClip([cropped_clip, username_clip, text_clip], size=phone_resolution)

            filename = form.cleaned_data['filename']
            output_dir = os.path.join("media", "processed_videos")
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{request.user}-{filename}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            relative_video_path = f"processed_videos/{output_filename}"
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

            ProcessedVideo.objects.create(title=filename, user=request.user, video_path=relative_video_path)
            # Read the video file
            processed_videos = [(f"/media/processed_videos/{output_filename}")]


            return render(request, 'create_oneCustomVid.html', {'videos': processed_videos})

    else:
        form = OneVidCustomForm()

    fonts = FontsChoose.objects.all()
    voices = VoiceChoose.objects.all()
    background_videos = BackgroundVideo.objects.all()
    return render(request, 'create_oneCustomVid.html', {'form': form, 'fonts': fonts,})

def create_reel(request):

    if request.method == 'POST':
        struggling_character = request.FILES['struggling_character']
        image1 = request.FILES['image1']
        image2 = request.FILES['image2']
        image3 = request.FILES['image3']
        text1 = request.POST['text1']
        text2 = request.POST['text2']
        text3 = request.POST['text3']
        text4 = request.POST['text4']
        selected_font_id = request.POST['selected_font']
        producer_tag = request.POST['producer_tag']

        selected_font = FontsChoose.objects.get(id=selected_font_id)

        final_clip = generate_motivation_reel(struggling_character, image1, image2, image3, text1, text2, text3, text4, selected_font, producer_tag)

        filename = request.POST['filename']
        output_dir = os.path.join("media", "processed_videos")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{request.user}-{filename}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        relative_video_path = f"processed_videos/{output_filename}"
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

        ProcessedVideo.objects.create(title=filename, user=request.user, video_path=relative_video_path)
        # Read the video file
        processed_videos = [(f"/media/processed_videos/{output_filename}")]


        return render(request, 'create_reel.html', {'videos': processed_videos})       

    #things to pass to the html form 
    fonts = FontsChoose.objects.all()
    return render(request, 'create_reel.html', {'fonts': fonts})

def generate_motivation_reel(struggling_character, image1, image2, image3, text1, text2, text3, text4, selected_font, producer_tag):
    # Define the screen resolution suitable for phones (e.g., TikTok or Instagram Reels)
    phone_resolution = (1080, 1920)  # width, height (portrait orientation)

    # Define the duration for each slide
    slide_duration = 5  # in seconds

    # Create a temporary directory to save the uploaded images
    temp_dir = tempfile.mkdtemp()

    try:
        # Save the uploaded images to temporary files
        struggling_character_path = os.path.join(temp_dir, struggling_character.name)
        with open(struggling_character_path, 'wb') as f:
            for chunk in struggling_character.chunks():
                f.write(chunk)

        image1_path = os.path.join(temp_dir, image1.name)
        with open(image1_path, 'wb') as f:
            for chunk in image1.chunks():
                f.write(chunk)

        image2_path = os.path.join(temp_dir, image2.name)
        with open(image2_path, 'wb') as f:
            for chunk in image2.chunks():
                f.write(chunk)

        image3_path = os.path.join(temp_dir, image3.name)
        with open(image3_path, 'wb') as f:
            for chunk in image3.chunks():
                f.write(chunk)

        # Generate the motivation reel using MoviePy script
        final_clip = generate_motivation_reel_from_files(struggling_character_path, image1_path, image2_path, image3_path, text1, text2, text3, text4, selected_font, producer_tag)

        return final_clip

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def generate_motivation_reel_from_files(struggling_character, image1, image2, image3, text1, text2, text3, text4, selected_font, producer_tag):
    # Define the screen resolution suitable for phones (e.g., TikTok or Instagram Reels)
    phone_resolution = (1080, 1920)  # width, height (portrait orientation)

    # Define the duration for each slide
    slide_duration = 5  # in seconds

    # Function to wrap text
    def wrap_text(text, width=28):
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if len(line + ' ' + word) <= width:
                line += ' ' + word
            else:
                lines.append(line.strip())
                line = word
        lines.append(line.strip())
        return '\n'.join(lines)

    # Create TextClips for each slide with sequential start times
    font_path = selected_font.font.path

    # First Slide: Struggling Character
    y_position = phone_resolution[1] // 2
    first_slide_duration = 4
    original_width, original_height = ImageClip(struggling_character).size
    background_clip = ColorClip(size=phone_resolution, color=(245, 245, 220)).set_duration(first_slide_duration)
    struggling_character_clip = ImageClip(struggling_character).resize(newsize=(original_width * 1.5, original_height * 1.5)).set_duration(first_slide_duration).set_position(('center', y_position-250))
    wrapped_text = wrap_text(text1)
    struggling_text_clip = TextClip(wrapped_text, fontsize=65, color='white', font=font_path, stroke_color='black', stroke_width=2, align='center').set_duration(first_slide_duration).set_position(('center', y_position))
    first_slide = CompositeVideoClip([background_clip, struggling_character_clip, struggling_text_clip], size=phone_resolution).set_duration(first_slide_duration)

    # Second Slide
    second_image = ImageClip(image1).resize(newsize=phone_resolution).set_duration(slide_duration)
    wrapped_second_text = wrap_text(text2)
    second_text_clip = TextClip(wrapped_second_text, fontsize=65, color='white', font=font_path, stroke_color='black', stroke_width=2, align='center').set_duration(slide_duration).set_position(('center', y_position-110))
    second_slide = CompositeVideoClip([second_image, second_text_clip], size=phone_resolution).set_duration(slide_duration)

    # Third Slide
    third_image = ImageClip(image2).resize(newsize=phone_resolution).set_duration(slide_duration)
    wrapped_third_text = wrap_text(text3)
    third_text_clip = TextClip(wrapped_third_text, fontsize=65, color='white', font=font_path, stroke_color='black', stroke_width=2, align='center').set_duration(slide_duration).set_position(('center', y_position-110))
    third_slide = CompositeVideoClip([third_image, third_text_clip], size=phone_resolution).set_duration(slide_duration)

    # Fourth Slide
    fourth_image = ImageClip(image3).resize(newsize=phone_resolution).set_duration(slide_duration)
    wrapped_fourth_text = wrap_text(text4)
    fourth_text_clip = TextClip(wrapped_fourth_text, fontsize=65, color='white', font=font_path, stroke_color='black', stroke_width=2, align='center').set_duration(slide_duration).set_position(('center', y_position-110))
    fourth_slide = CompositeVideoClip([fourth_image, fourth_text_clip], size=phone_resolution).set_duration(slide_duration)

    # Combine all slides into one sequence
    final_clip = CompositeVideoClip([first_slide, second_slide.set_start(first_slide_duration), 
                                     third_slide.set_start(first_slide_duration + slide_duration), 
                                     fourth_slide.set_start(first_slide_duration + 2 * slide_duration)])

    # Add a user tag textbox throughout the entire reel
    username_clip = TextClip(f"{producer_tag}", fontsize=40, color='white', font=font_path).set_position(('center', phone_resolution[1] - 200))

    # Set the duration of the username clip to match the final composition
    username_clip = username_clip.set_duration(final_clip.duration)

    # Add the username clip to the final composition
    final_clip = CompositeVideoClip([final_clip, username_clip])

    return final_clip


def create_onePic(request):
    if request.method == 'POST':
        onePic = request.FILES['onePic']
        text1 = request.POST['text1']
        selected_font_id = request.POST['selected_font']
        producer_tag = request.POST['producer_tag']

        selected_font = FontsChoose.objects.get(id=selected_font_id)

        final_clip = generate_onePic_reel(onePic, text1, selected_font, producer_tag)


        filename = request.POST['filename']
        output_dir = os.path.join("media", "processed_videos")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{request.user}-{filename}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        relative_video_path = f"processed_videos/{output_filename}"
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

        ProcessedVideo.objects.create(title=filename, user=request.user, video_path=relative_video_path)
        # Read the video file
        processed_videos = [(f"/media/processed_videos/{output_filename}")]


        return render(request, 'create_onePic.html', {'videos': processed_videos})       


    fonts = FontsChoose.objects.all()
    return render(request, 'create_onePic.html', {'fonts': fonts})

def generate_onePic_reel(onePic, text1, selected_font, producer_tag):
    # Define the screen resolution suitable for phones (e.g., TikTok or Instagram Reels)
    phone_resolution = (1080, 1920)  # width, height (portrait orientation)

    # Create a temporary directory to save the uploaded images
    temp_dir = tempfile.mkdtemp()
    onePicPath = os.path.join(temp_dir, onePic.name)
    try:
        # Save the uploaded image to a temporary file
        with open(onePicPath, 'wb') as f:
            for chunk in onePic.chunks():
                f.write(chunk)

        # Generate the motivation reel using MoviePy script
        final_clip = generate_onePic_reel_from_files(onePicPath, text1, selected_font, producer_tag)

        return final_clip

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def generate_onePic_reel_from_files(onePicPath, text1, selected_font, producer_tag):
    phone_resolution = (1080, 1920)  # width, height (portrait orientation)

    # Define the duration for the fade in and out and the total display time
    fade_duration = 1  # duration of fade in and fade out
    display_duration = 6  # total duration the image will be visible

    # Function to wrap text
    def wrap_text(text, width=33):
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if len(line + ' ' + word) <= width:
                line += ' ' + word
            else:
                lines.append(line.strip())
                line = word
        lines.append(line.strip())
        return '\n'.join(lines)

    # Wrap the text
    wrapped_text = wrap_text(text1)

    # Create an image clip and resize it
    image_clip = ImageClip(onePicPath).resize(width=phone_resolution[0]).set_duration(display_duration)

    # Path to the font
    font_path = selected_font.font.path

    # Create a text clip
    text_clip = TextClip(wrapped_text, fontsize=60, color='white', font=font_path, stroke_color='black', stroke_width=2, align='center').set_duration(display_duration)

    # Create a background clip to make the transition smooth
    background_clip = ColorClip(size=phone_resolution, color=(0, 0, 0)).set_duration(display_duration + 2 * fade_duration)

    # Apply fade-in and fade-out effects to both text and image
    image_clip = image_clip.set_position(("center", phone_resolution[1] * 0.3)).fadein(fade_duration).fadeout(fade_duration)
    text_clip = text_clip.set_position(("center", phone_resolution[1] * 0.1)).fadein(fade_duration).fadeout(fade_duration)

    # Composite the image and text onto the background
    composite_clip = CompositeVideoClip([background_clip, image_clip, text_clip])

    # Add a user tag textbox throughout the entire reel
    username_clip = TextClip(f"{producer_tag}", fontsize=40, color='white', font=font_path, stroke_color='black', stroke_width=2).set_position(('center', phone_resolution[1] - 100)).set_duration(composite_clip.duration)
    final_clip = CompositeVideoClip([composite_clip, username_clip])

    return final_clip






