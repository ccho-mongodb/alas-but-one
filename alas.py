import importlib, json

def get_stage(module_name, config):
    modulename = config['modules'][module_name]['path']
    funcname = config['modules'][module_name]['funcName']
    module = importlib.import_module(modulename)
    return getattr(module, funcname)


def main():
    with open('config.json') as f:
        config = json.load(f)

    try:
        MAX_OCCURRENCE=config['maxOccurrences']
        REPO = "nodejs"

        # File location setup
        repo_config = config['docs'][REPO]
        name = repo_config['name']
        directory = config['repo_base_full_path'] + repo_config['relative_path'] + repo_config['source_dir']

        # Read data
        collector = get_stage('collector', config)
        reader = get_stage('reader', config)

        # Tokenize data
        tokenizer = get_stage('tokenizer', config)

        # Filter by max occurrences
        max_occur_matcher = get_stage('max_occurrence_matcher', config)

        # Add spellcheck data
        spell_checker = get_stage('spell_checker', config)

        # Format output
        formatter = get_stage('formatter', config)


        candidate_files = collector(directory)
        content = reader(candidate_files)
        token_dict = tokenizer(content, REPO)
        token_dict = max_occur_matcher(token_dict, MAX_OCCURRENCE)
        spell_checker(token_dict)

        formatter(token_dict.values())

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
