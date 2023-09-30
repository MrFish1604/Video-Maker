from sys import argv
import requests
from html.parser import HTMLParser


if len(argv)<2:
    exit(1)

title = argv[1]
URL = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={title}&prop=extracts&exintro&explaintext"

print(URL)
response = requests.get(URL)

if(not response.ok):
    print("Status:", response.status_code)
    exit(response.status_code)

r = response.json()["query"]["pages"]
extracted = ""
for v in r.values():
    extracted = v["extract"]

print(extracted)