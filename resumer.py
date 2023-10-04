from gpt4all import GPT4All
from sys import argv, stdout, stdin
from contextlib import redirect_stdout
from pathlib import Path
from hashlib import md5
from utils import printb

printb("Resumer")

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

# system_template = "Resume the text given to you in simpler words. Be accurate."
# system_template = "Resume the text given to you in an entertaining way for children."
# system_template = "You job is to summarize texts given to you. Be accurate."
# system_template = "TLDR:"
header = """ As a professional summarizer, create a concise and comprehensive summary of the provided text, be it an article, post, conversation, or passage, while adhering to these guidelines:
    1. Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness.
    2. Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects.
    3. Rely strictly on the provided text, without including external information.
    4. Format the summary in paragraph form for easy understanding.
    5. Conclude your notes with [End of Notes, Message #X] to indicate completion, where "X" represents the total number of messages that I have sent. In other words, include a message counter where you start with #1 and add 1 to the message counter every time I send a message.

By following this optimized prompt, you will generate an effective summary that encapsulates the essence of the given text in a clear, concise, and reader-friendly manner.
"""
# system_template = "List the 3 main concepts of this text. Max 2 words per item."
# system_template = "Describe 3 images of the 3 main concepts of the following text."
system_template = ""
# system_template = "You are an AI assistant. Help as much as you can."
cache_filename = md5(("explainer" + text_input + system_template).encode('utf-8')).hexdigest()
if (gpt_cache_p / cache_filename).exists():
    print("Resumer uses cache")
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

output = ""
with model.chat_session():
    print(model.current_chat_session)
    try:
        with open("output.txt", "w") as wfile:
            print("0"*9)
            for token in model.generate("TLDR: " + text_input, temp=1, max_tokens=200, streaming=False):
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
