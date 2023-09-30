from sys import stdin
from utils import *
from numpy import array
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips
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
for s in sentences:
    print(f"{iplot}/{N}")
    status, img = fetch_image_from_sd_server(s)
    if(status!=200):
        print("SD ERROR:", status)
    imgs += [img]*FPS*(int(audio_clips[iplot-1].duration))
    plt.subplot(N*10 + 100 + iplot)
    plt.imshow(imgs[-1])
    iplot+=1
plt.show(block=True)

clip = ImageSequenceClip(imgs, fps=FPS)
clip = clip.set_audio(audio_clip)
clip.write_videofile("output.mp4", fps=FPS)
# clip.preview()