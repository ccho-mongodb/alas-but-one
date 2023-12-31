import os, importlib, json

def get_stage(module_name, config):
    modulename = config['modules'][module_name]['path']
    funcname = config['modules'][module_name]['funcName']
    module = importlib.import_module(modulename)
    return getattr(module, funcname)


def main():
    with open('config.json') as f:
        config = json.load(f)

    try:
        MAX_OCCURRENCE = config['maxOccurrences']
        MONGODB_URI = os.environ['ABO_MONGO_URI']

        REPO_BASE_PATH = config['repo_base_full_path']
        IGNORE_DB_NAME = config['ignore_list']['database']
        IGNORE_COLL_NAME = config['ignore_list']['collection']
        REPOS = config['docs']

        for repo_config in REPOS.items():
            # File location setup
            name = repo_config[0]
            cfg = repo_config[1]
            directory = REPO_BASE_PATH + cfg['relative_path'] + cfg['source_dir']

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

            # Run stages
            # TODO: add pre and post condition dataclasses for each stage
            candidate_files = collector(directory)
            content = reader(candidate_files)
            token_dict = tokenizer(content, cfg)
            token_dict = max_occur_matcher(token_dict, MAX_OCCURRENCE)
            spell_checker(token_dict)
            ignore_list(token_dict, cfg, MONGODB_URI, IGNORE_DB_NAME, IGNORE_COLL_NAME)
            formatter(token_dict.values(), "%s.csv" % name)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
