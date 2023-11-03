from sys import stdin, argv
from utils import *
from numpy import array
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import all as vfx
import matplotlib.pyplot as plt

FPS = 24

img_options = {"batch_size":1}
if len(argv)>1:
    for arg in argv[1:]:
        op = arg.split('=')
        if len(op)!=2:
            continue
        img_options[op[0]] = op[1]

print(f"Images Options : {img_options}")
printb("\nReading input stream...\n")
sentences = read_sentences(stdin)
N = len(sentences)
if N<1:
    printb("ERROR: No input data")
    exit(2)
print(f"Nbr sentences: {len(sentences)}")
print(sentences)

printb("\nGenerating audio...")
wav_files = [my_tts(s) for s in sentences]
audio_clips = [AudioFileClip(wav) for wav in wav_files]
audio_clip = concatenate_audioclips(audio_clips)

printb("\nGenerating images...")
iplot = 1
imgs: list[array] = []
text_clips:list[TextClip] = []
img_clips:list[ImageSequenceClip] = []
duration = 0
fontsize = calc_fontsize(int(img_options.get("height", img_options.get("width", SIZE[1]))))
for s in sentences:
    print(f"{iplot}/{N}")
    status, img = fetch_image_from_sd_server(s, options=img_options)
    if(status!=200):
        printb("SD ERROR:", status)
        exit(3)
    imgs = [img[0]]*round(FPS/len(img))*(int(audio_clips[iplot-1].duration + 0.5))
    for i in img[1:]:
        imgs += [i]*round(FPS/len(img))*(int(audio_clips[iplot-1].duration + 0.5))
    seq:ImageSequenceClip = ImageSequenceClip(imgs, fps=FPS)
    text_options = {"color":"White", "font":"Comic-Neue-Bold", "fontsize":fontsize}
    words = cut_str(s)
    h = (1)*seq.duration/(len(words)+1)
    # text_clip = TextClip("".join([a if a!=' ' else '\n' for a in s]), color="White", font="Comic-Neue-Bold", fontsize=25)
    # text_clip:TextClip = text_clip.set_position(("center","center"))
    # text_clip:TextClip = text_clip.set_duration(seq.duration
    seq = seq.set_start(duration, change_end=True).fx(vfx.fadeout, duration=0.2).fx(vfx.fadein, duration=0.2).set_position(move_img)
    img_clips.append(seq)
    text_clips += [(
        TextClip(words[i], **text_options)
        .set_position(("center",)*2)
        .set_duration(h)
        .set_start(duration + i*h, change_end=True)
        ) for i in range(len(words)) if not words[i] in [' ', '\n', '']]
    duration += seq.duration
    iplot+=1

# clip = ImageSequenceClip(imgs, fps=FPS)
# clip = concatenate_videoclips(img_clips)
clip:CompositeVideoClip = CompositeVideoClip(img_clips + text_clips, size=SIZE)
clip = clip.set_audio(audio_clip)
clip.set_duration(duration).write_videofile("output.mp4", fps=FPS)
# clip.preview()