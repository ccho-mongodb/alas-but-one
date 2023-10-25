import sys, os, re
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from models.token import Token
from models.token_location import TokenLocation

# Match all word character strings unless they start with certain characters
WORD_REGEX=re.compile(r'\b(?![_\-0-9])[A-Za-z0-9\']+\b')

def run(content_dict, repo):
    token_dict = {}

    for key in content_dict:
        lines = content_dict[key].lower().split('\n')
        for i, line in enumerate(lines):
            for word in re.findall(WORD_REGEX, line):
                if word in token_dict:
                    token = token_dict[word]
                    token.locations.append(TokenLocation(key, i))
                else:
                    token_dict[word] = Token(word, repo, [ TokenLocation(key, i) ])

    return token_dict
