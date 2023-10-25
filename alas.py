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
        IGNORE_DB_NAME = config['ignore_list']['database']
        IGNORE_COLL_NAME = config['ignore_list']['collection']

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

        # Add ignore list data
        ignore_list = get_stage('ignore_list_matcher', config)

        # Format output
        formatter = get_stage('formatter', config)

        candidate_files = collector(directory)
        content = reader(candidate_files)
        token_dict = tokenizer(content, REPO)
        token_dict = max_occur_matcher(token_dict, MAX_OCCURRENCE)
        spell_checker(token_dict)
        ignore_list(token_dict, REPO, IGNORE_DB_NAME, IGNORE_COLL_NAME)

        formatter(token_dict.values())

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
