import os

def run(paths):
    data = {}
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            data[path] = f.read()

    return data
