import os, importlib, json
from pipeline import Pipeline

def get_stage(module_name, config):
    modulename = config['modules'][module_name]['path']
    funcname = config['modules'][module_name]['funcName']
    module = importlib.import_module(modulename)
    return getattr(module, funcname)


def main():
    with open('config.json') as f:
        config = json.load(f)
    
    settings_config = config['settings']
    modules_config = config['modules']

    try:
        for repo_name, repo_config in config['repositories'].items():
            pipeline = Pipeline(settings_config, repo_config, modules_config)

            pipeline.add_task('collector')
            pipeline.add_task('reader')
            pipeline.add_task('tokenizer')
            pipeline.add_task('max_occurrence_matcher')
            pipeline.add_task('spell_checker')
            pipeline.add_task("ignore_list_matcher")
            pipeline.add_task('formatter')

            directory = settings_config['repo_base_full_path'] + repo_config['relative_path'] + repo_config['source_dir']
            result = pipeline.run(directory)

            print(f"Processed {repo_name}: {result}")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
