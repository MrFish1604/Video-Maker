from gpt4all import GPT4All
from sys import argv, stdout

if len(argv)<2:
    exit(1)
with open(argv[1]) as rfile:
    text_input = rfile.read()

print(text_input)
print()

model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin")

# system_template = "You are to resume the text given to you. Be accurate."
# system_template = "You are to resume the text given to you in an entertaining way for children."
system_template = "List the 3 main concepts of this text. Max 2 words per item."
# system_template = "Describe 3 images of the 3 main concepts of the following text."

with model.chat_session(system_prompt=system_template):
    print(model.current_chat_session)
    try:
        with open("output.txt", "w") as wfile:
            for token in model.generate(text_input, temp=0.5, max_tokens=50, streaming=True):
                print(token, end="")
                wfile.write(token)
                stdout.flush()
        print()
    except EOFError:
        exit(3)
    except KeyboardInterrupt:
        exit(2)