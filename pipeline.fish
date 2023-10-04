argparse "F/fact" -- $argv
if set -q _flag_fact
	py wikipedia_extractor.py $argv[1] | py resumer.py
else
	py explainer.py $argv[1]
end
cat output.txt | py make_video.py $argv[2..]
