from gpt4all import GPT4All
from sys import argv, stdout, stdin
from contextlib import redirect_stdout
from pathlib import Path
from hashlib import md5

cache_p = Path(".cache")
if not cache_p.exists():
    Path.mkdir(cache_p)

gpt_cache_p = cache_p/"gpt"
if not gpt_cache_p.exists():
    Path.mkdir(gpt_cache_p)

text_input = ""
if len(argv)<2:
    text_input = stdin.read()
else:
    with open(argv[1]) as rfile:
        text_input = rfile.read()

cache_filename = md5(text_input.encode('utf-8')).hexdigest()
if (gpt_cache_p / cache_filename).exists():
    print("Resumer uses cache")
    with open(gpt_cache_p/cache_filename, 'r') as rfile:
        with open("output.txt", "w") as wfile:
            output = rfile.read()
            print(output)
            wfile.write(output)
        exit(0)

# print(text_input)
# print()

model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin")

system_template = "Resume the text given to you in simpler words. Be accurate."
# system_template = "Resume the text given to you in an entertaining way for children."
# system_template = "List the 3 main concepts of this text. Max 2 words per item."
# system_template = "Describe 3 images of the 3 main concepts of the following text."

output = ""
with model.chat_session(system_prompt=system_template):
    print(model.current_chat_session)
    try:
        with open("output.txt", "w") as wfile:
            print("0"*9)
            for token in model.generate(text_input, temp=0.5, max_tokens=200, streaming=True):
                print(token, end="")
                output+=token
                wfile.write(token)
                stdout.flush()
        print()
    except EOFError:
        exit(3)
    except KeyboardInterrupt:
        exit(2)

with open(gpt_cache_p/cache_filename, 'w') as wfile:
    wfile.write(output)
