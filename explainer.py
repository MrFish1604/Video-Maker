from gpt4all import GPT4All
from sys import argv, stdout, stdin
from pathlib import Path
from hashlib import md5
from utils import printb

printb("Explainer\n")

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
    text_input = argv[1]
system_template = ""
# system_template = "You are an AI assistant. Help as much as you can."
cache_filename = md5(("resumer" + text_input + system_template).encode('utf-8')).hexdigest()
if (gpt_cache_p / cache_filename).exists():
    print("Explainer uses cache")
    with open(gpt_cache_p/cache_filename, 'r') as rfile:
        with open("output.txt", "w") as wfile:
            output = rfile.read()
            print(output)
            wfile.write(output)
        exit(0)

print(text_input)
print()

model_name = "orca-mini-3b.ggmlv3.q4_0.bin"
printb(f"Loading LLM model({model_name})...")
model = GPT4All(model_name, allow_download=False)
printb("Model loaded.")

input_template = "Explanations about {}:"
print(f'input_template = "{input_template}"')
output = ""
try:
    with open("output.txt", "w") as wfile:
        print("0"*9)
        for token in model.generate(input_template.format(text_input) + text_input, temp=1, max_tokens=200, streaming=False):
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
