import sys, os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from models.token import Token

def run(token_dict, num_occurrences):

    filtered_token_dict = {}

    for word, token in token_dict.items():
        if len(token.locations) <= num_occurrences:
            filtered_token_dict[word] = token

    return filtered_token_dict

