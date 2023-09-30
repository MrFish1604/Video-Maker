from gpt4all import GPT4All
from sys import argv, stdout, stdin
from contextlib import redirect_stdout

text_input = ""
if len(argv)<2:
    text_input = stdin.read()
else:
    with open(argv[1]) as rfile:
        text_input = rfile.read()

# print(text_input)
# print()

model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin")

system_template = "Resume the text given to you in simpler words. Be accurate."
# system_template = "Resume the text given to you in an entertaining way for children."
# system_template = "List the 3 main concepts of this text. Max 2 words per item."
# system_template = "Describe 3 images of the 3 main concepts of the following text."

with model.chat_session(system_prompt=system_template):
    print(model.current_chat_session)
    try:
        with open("output.txt", "w") as wfile:
            print("0"*9)
            for token in model.generate(text_input, temp=0.5, max_tokens=200, streaming=True):
                print(token, end="")
                wfile.write(token)
                stdout.flush()
        print()
    except EOFError:
        exit(3)
    except KeyboardInterrupt:
        exit(2)