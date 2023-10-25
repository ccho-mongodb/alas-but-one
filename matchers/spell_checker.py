from spellchecker import SpellChecker

def run(token_dict):
    checker = SpellChecker()

    misspelled = checker.unknown(token_dict.keys())

    for word, token in token_dict.items():
        if word in misspelled:
            token.misspelled = True
        else:
           token.misspelled = False

