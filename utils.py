from typing import TextIO
from numpy import array
import numpy as np
from hashlib import md5
import requests
from io import BytesIO
import base64
from PIL import Image, PngImagePlugin
from contextlib import redirect_stdout
from configreader import *
from pathlib import Path
from multiprocessing import Process, Queue
from time import sleep
from tqdm import tqdm

config = readconfig("config")
SD_ADDR = config.get("SD_ADDR", D_SD_ADDR)
SD_PORT = config.get("SD_PORT", D_SD_PORT)

cache_p = Path(".cache")
if not cache_p.exists():
    Path.mkdir(cache_p)
tts_cache_p = cache_p/Path("tts")
if not tts_cache_p.exists():
    Path.mkdir(tts_cache_p)

BOLD = '\033[1m'
ENDC = '\033[0m'

def printb(txt:str, *args, **kwargs):
    print(BOLD + txt + ENDC, *args, **kwargs)

def calc_fontsize(h:int) -> int:
    return 0.05*h

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

def pil_to_base64(pil_image: Image) -> str:
    """Encode PIL Image to base64 string."""
    with BytesIO() as stream:
        meta = PngImagePlugin.PngInfo()
        for k, v in pil_image.info.items():
            if isinstance(k, str) and isinstance(v, str):
                meta.add_text(k, v)
        pil_image.save(stream, "PNG", pnginfo=meta)
        base64_str = str(base64.b64encode(stream.getvalue()), "utf-8")
        return "data:image/png;base64," + base64_str

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
URL = f"http://{SD_ADDR}:{SD_PORT}"
OPTIONS = {
    'width': SIZE[0],
    'height': SIZE[1],
    'steps': 20
}
img_prompt_appendix = ""
def fetch_image_from_sd_server(prompt:str, options:dict=dict(), url:str=URL, progress_bar:bool=True) -> tuple[int, array]:
    payload = OPTIONS.copy()
    payload.update(options)
    if "height" in options and not "width" in options:
        payload["width"] = 1 + int(int(payload["height"])*ratio)
    elif not "height" in options and "width" in options:
        payload['height'] = 1 + int(int(payload["width"])/ratio)
    payload["prompt"] = prompt + img_prompt_appendix
    upscale = False
    if int(payload["width"])*int(payload["height"]) > 150_000:
        print("SD will use an upscaler")
        upscale = True
        expected_width = payload["width"]
        expected_height = payload["height"]
        payload["width"] = 512
        payload['height'] = 1 + int(int(payload["width"])/ratio)
    print("payload=", payload)
    if progress_bar:
        def make_req_for_img(q:Queue):
            r = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
            q.put(r)
        pq = Queue()
        p = Process(target=make_req_for_img, args=(pq,))
        p.start()
        last_progress = 0
        pbar = tqdm(total=100)
        while pq.empty():
            prog_req = requests.get(url=f"{url}/sdapi/v1/progress")
            if not prog_req:
                p.kill()
                return 444, array(444)
            progress = round(prog_req.json().get('progress')*100, 1)
            pbar.update(progress - last_progress)
            last_progress = progress
            sleep(0.1)
        pbar.update(100 - last_progress)
        pbar.close()
        # print()
        response = pq.get()
    else:
        response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    if not response.ok:
        print(response.json())
        return response.status_code, array(0)
    r = response.json()
    if upscale:
        print("Upscaling...")
        upscaler_payload = {
            "upscaler_1": "ESRGAN_4x",
            "upscaling_resize": 2,
            "upscaling_crop": "false",
            "imageList" : [{"data":r['images'][i], "name":str(i)} for i in range(len(r['images']))]
        }
        response = requests.post(url = f"{url}/sdapi/v1/extra-batch-images", json=upscaler_payload)
        r = response.json()
    if not response.ok:
        print(response.json())
        return response.status_code, array(0)
    images:list = [array(Image.open(BytesIO(base64.b64decode(img)))) for img in r['images']]
    return response.status_code, images
    # return 200, array(Image.open(f"{prompt[:4]}.png"))

tts = None
tts_loaded = False
def load_TTS_module():
    global tts
    global tts_loaded
    printb("Loading TTS module...\n")
    from TTS.api import TTS
    # model_name = TTS().list_models()[1]
    model_name = 'tts_models/en/ljspeech/tacotron2-DDC_ph'
    with open("/dev/null", 'w') as nullfile:
        with redirect_stdout(nullfile):
            tts = TTS(model_name).to("cpu")
    tts_loaded = True

def my_tts(txt:str):
    # print(f"TTS \"{txt}\"...")
    rtn = f"tts_{md5(txt.encode('utf-8')).hexdigest()[:4]}.wav"
    if (tts_cache_p/rtn).exists():
        print("TTS uses cache")
        return (tts_cache_p/rtn).as_posix()
    if not tts_loaded:
        load_TTS_module()
    # tts.tts_to_file(txt, speaker=tts.speakers[0], language=tts.languages[0], file_path=rtn, speed=10)
    tts.tts_to_file(txt, file_path=(tts_cache_p/rtn))
    return (tts_cache_p/rtn).as_posix()

def cut_str(txt:str, N:int=15) -> list[str]:
    rtn = [""]
    for a in txt.split(' '):
        if len(rtn[-1]) >= N:
            rtn.append("")
        rtn[-1] += a + " "
    return rtn