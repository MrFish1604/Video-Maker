# Video Maker
An **AI** powered **video maker** that creates videos from a **single word**.

## Usage
Create a file named `config` on the project's root.
```sh
SD_ADDR=127.0.0.1 # Or whatever address your SD server's using
SD_PORT=7860    # Or whatever port your SD server's listening on.
```
```sh
# For bash/zsh users
py wikipedia_extractor.py <subject> | py resumer.py
cat output.txt | py make_video.py [option1=value1 option2=value2 ...]
```

```sh
# For fish users
fish pipeline.fish <subject> [option1=value1 option2=value2 ...]
```
The video should be named `output.mp4`.

## Installation
You need a server running [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui).
1. Clone the repository
```sh
git clone https://github.com/MrFish1604/video_maker.git
```
2. Create a new virtual environnemnt
```sh
# For bash/zsh users
python -m venv video_maker
source env/bin/activate
```
```sh
# For fish users (install virtualfish first)
vf new video_maker
```

3. Install dependencies
```sh
sudo apt update
sudo apt install imagemagick
pip install -r requirements.txt
```

## Dependencies
This project uses :
1. [GPT4All](https://gpt4all.io/index.html)
2. [TTS From Coqui-AI](https://github.com/coqui-ai/TTS)
3. [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)