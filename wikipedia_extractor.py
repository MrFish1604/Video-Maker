from sys import argv
import requests
from html.parser import HTMLParser
from pathlib import Path


if len(argv)<2:
    exit(1)

title = argv[1]

cache_p = Path(".cache")
if not cache_p.exists():
    Path.mkdir(cache_p)

for p in cache_p.iterdir():
    if p.name == title:
        with open(p, 'r') as rfile:
            print(rfile.read())
            exit(0)
URL = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={title}&prop=extracts&exintro&explaintext"

# print(URL)
response = requests.get(URL)

if(not response.ok):
    print("Status:", response.status_code)
    exit(response.status_code)

r = response.json()["query"]["pages"]
extracted = ""
for v in r.values():
    extracted = v["extract"]

print(extracted)

with open(cache_p / title, 'w') as wfile:
    wfile.write(extracted)