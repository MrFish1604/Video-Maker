from sys import stdin
from utils import *
from numpy import array
from moviepy.editor import ImageSequenceClip
import matplotlib.pyplot as plt

FPS = 24

sentences = read_sentences(stdin)
print(f"Nbr sentences: {len(sentences)}")
print(sentences)

print("Generating images...")
iplot = 1
imgs: list[array] = []
for s in sentences:
    img = get_image_from_text(s)
    imgs += [img]*FPS
    plt.subplot(len(sentences)*10 + 100 + iplot)
    plt.imshow(imgs[-1])
    iplot+=1
plt.show()

clip = ImageSequenceClip(imgs, fps=FPS)
clip.write_videofile("output.mp4", fps=FPS)