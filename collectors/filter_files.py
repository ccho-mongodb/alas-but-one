import os, re

def run(directory):
    paths = []

    filename_re = r'\.(txt|rst)$'

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if re.search(filename_re, filename):
                paths.append(os.path.join(root,filename))

    return paths
