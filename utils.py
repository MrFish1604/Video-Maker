from typing import TextIO
from numpy import array
import numpy as np

def read_sentences(stream: TextIO) -> list[str]:
    sentences = [""]
    a = stream.read(1)
    while a:
        if a in ['.', '?', '!', ';', ':']:
            sentences[-1] += a
            sentences.append("")
        else:
            sentences[-1] += a
        a = stream.read(1)
    return sentences

def get_image_from_text(txt: str, size:tuple[int]=(256, 256)) -> array:
    img = np.zeros(size+(3,), dtype=int)
    j = 0
    c = 0
    for a in txt:
        img[ord(a)%256, j, c] = 255
        j += 1
        if j==size[1]:
            c += 1
            c = c%3
            j=0
    return img