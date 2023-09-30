from typing import TextIO
from numpy import array
import numpy as np
from hashlib import md5
import requests
import io
import base64
from PIL import Image

print("Loading TTS module...")
from TTS.api import TTS

def read_sentences(stream: TextIO) -> list[str]:
    sentences = []
    a = stream.read(1)
    c = 9
    while c!=9:
        if a=='0':
            c += 1
        else:
            c = 0
        a = stream.read(1)
    buff = ""
    while a:
        if a in ['.', '?', '!', ';', ':']:
            buff+=a
            sentences.append(buff)
            buff = ""
        else:
            buff += a
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

ratio = 9/16
__x = 256
SIZE = (__x, int(1 + __x/ratio))
URL = "http://192.168.1.16:7860"
OPTIONS = {
    'width': SIZE[0],
    'height': SIZE[1],
    'steps': 20
}
def fetch_image_from_sd_server(prompt:str, options:dict=OPTIONS, url:str=URL) -> tuple[int, array]:
    options["prompt"] = prompt + " Realistic photograph"
    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=options)
    if not response.ok:
        return response.status_code, array(0)
    r = response.json()
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    image.save(f"{prompt[:4]}.png")
    rtn = array(image)
    return response.status_code, rtn
    # return 200, array(Image.open(f"{prompt[:4]}.png"))

# model_name = TTS().list_models()[1]
model_name = 'tts_models/en/ljspeech/tacotron2-DDC_ph'
tts = TTS(model_name).to("cpu")

def my_tts(txt:str):
    # print(f"TTS \"{txt}\"...")
    rtn = f"tts_{md5(txt.encode('utf-8')).hexdigest()[:4]}.wav"
    # tts.tts_to_file(txt, speaker=tts.speakers[0], language=tts.languages[0], file_path=rtn, speed=10)
    tts.tts_to_file(txt, file_path=rtn)
    return rtn

def cut_str(txt:str, N:int=15) -> list[str]:
    rtn = [""]
    for a in txt.split(' '):
        if len(rtn[-1]) >= N:
            rtn.append("")
        rtn[-1] += a + " "
    return rtn