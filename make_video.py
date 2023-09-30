from sys import stdin
from utils import *
from numpy import array
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips, TextClip, CompositeVideoClip, concatenate_videoclips
import matplotlib.pyplot as plt

FPS = 24

print("Reading input stream...")
sentences = read_sentences(stdin)
N = len(sentences)
print(f"Nbr sentences: {len(sentences)}")
print(sentences)

print("Generating audio...")
wav_files = [my_tts(s) for s in sentences]
audio_clips = [AudioFileClip(wav) for wav in wav_files]
audio_clip = concatenate_audioclips(audio_clips)

print("Generating images...")
iplot = 1
imgs: list[array] = []
text_clips:list[TextClip] = []
img_clips:list[ImageSequenceClip] = []
duration = 0
for s in sentences:
    print(f"{iplot}/{N}")
    status, img = fetch_image_from_sd_server(s)
    if(status!=200):
        print("SD ERROR:", status)
    imgs = [img]*FPS*(int(audio_clips[iplot-1].duration))
    seq = ImageSequenceClip(imgs, fps=FPS)
    text_clip = TextClip(s)
    text_clip:TextClip = text_clip.set_position(("center","center"))
    text_clip:TextClip = text_clip.set_duration(seq.duration)
    if len(img_clips)==0:
        img_clips.append(seq)
        text_clips.append(text_clip)
    else:
        img_clips.append(seq.set_start(duration, change_end=True))
        text_clips.append(text_clip.set_start(duration, change_end=True))
    duration += seq.duration
    iplot+=1

# clip = ImageSequenceClip(imgs, fps=FPS)
# clip = concatenate_videoclips(img_clips)
clip:CompositeVideoClip = CompositeVideoClip(img_clips + text_clips)
clip = clip.set_audio(audio_clip)
clip.set_duration(duration).write_videofile("output.mp4", fps=FPS)
# clip.preview()