py wikipedia_extractor.py $argv[1] | py resumer.py
cat output.txt | py make_video.py $argv[2..]