import glob
import itertools

files = glob.glob("input_data_files/battletome_txts/*")

with open('concattedtomes.txt', 'w') as outfile:
    for fname in files:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)