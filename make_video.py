from sys import stdin
from utils import *
from numpy import array
from moviepy.editor import ImageSequenceClip, AudioFileClip
import matplotlib.pyplot as plt

FPS = 24

print("Reading input stream...")
sentences = read_sentences(stdin)
print(f"Nbr sentences: {len(sentences)}")
print(sentences)

print("Generating audio...")
wav_file = my_tts(" ".join(sentences))
audio_clip = AudioFileClip(wav_file)

print("Generating images...")
iplot = 1
imgs: list[array] = []
for s in sentences:
    img = get_image_from_text(s)
    imgs += [img]*FPS*(int(audio_clip.duration/len(sentences))+2)
    plt.subplot(len(sentences)*10 + 100 + iplot)
    plt.imshow(imgs[-1])
    iplot+=1
plt.show()

clip = ImageSequenceClip(imgs, fps=FPS)
clip = clip.set_audio(audio_clip)
clip.write_videofile("output.mp4", fps=FPS)
# clip.preview()