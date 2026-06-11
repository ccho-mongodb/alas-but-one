"""
alas-but-one — atomic typo candidate finder for MongoDB documentation.

Usage:
  python alas.py                               # run all repos, JSONL output
  python alas.py --format csv                  # CSV output
  python alas.py --repo "Golang Driver Docs"   # single repo by display name
  python alas.py --ai                          # AI review of borderline tokens
  python alas.py --parallel                    # process repos concurrently
  python alas.py --verbose                     # per-stage token counts
  python alas.py --train labels.jsonl          # train classifier from labeled JSONL
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from pipeline import Pipeline
from ai.hooks import HookRegistry
from ai.reviewer import AIReviewer
from training.predictor import MLPredictor
from tasks.factory import TaskFactory


def load_config(path: str = 'config.json') -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def run_repo(
    repo_name: str,
    repo_config: Dict,
    settings_config: Dict,
    modules_config: Dict,
    output_format: str,
    ai_enabled: bool,
    predictor: MLPredictor,
    verbose: bool,
) -> str:
    hooks = HookRegistry()

    if verbose:
        @hooks.post_stage('tokenizer')
        def _log_tokenizer(stage, data):
            print(f"    tokenizer: {len(data)} unique tokens")
            return data

        @hooks.post_stage('max_occurrence_matcher')
        def _log_matcher(stage, data):
            print(f"    max_occurrence_matcher: {len(data)} candidates")
            return data

        @hooks.post_stage('spell_checker')
        def _log_spell(stage, data):
            misspelled = sum(1 for t in data.values() if t.misspelled)
            print(f"    spell_checker: {misspelled}/{len(data)} flagged misspelled")
            return data

    # Merge --ai flag into settings without mutating the original
    effective_settings = dict(settings_config)
    if ai_enabled:
        ai_cfg = dict(effective_settings.get('ai', {}))
        ai_cfg['enabled'] = True
        effective_settings = {**settings_config, 'ai': ai_cfg}

    directory = (
        effective_settings['repo_base_full_path']
        + repo_config['relative_path']
        + repo_config['source_dir']
    )

    # Main pipeline (everything except formatting)
    pipeline = Pipeline(effective_settings, repo_config, modules_config, hooks=hooks)
    pipeline.add_task('collector')
    pipeline.add_task('reader')
    pipeline.add_task('tokenizer')
    pipeline.add_task('max_occurrence_matcher')
    pipeline.add_task('spell_checker')
    pipeline.add_task('ignore_list_matcher')

    token_dict = pipeline.run(directory)
    content_map = pipeline.stage_results.get('reader', {})

    # ML confidence override (if a trained model exists)
    if predictor.available:
        token_dict = predictor.apply(token_dict)
        if verbose:
            print(f"    ml_predictor: confidence scores updated from {predictor.model_path}")

    # AI review of borderline tokens (confidence in review zone)
    reviewer = AIReviewer(effective_settings)
    token_dict = reviewer.run(token_dict, content_map)

    # Format and write output
    formatter_key = 'jsonl_formatter' if output_format == 'jsonl' else 'formatter'
    formatter = TaskFactory.create_task(
        formatter_key, effective_settings, repo_config, modules_config
    )
    return formatter.run(token_dict)


def cmd_run(args, config: Dict) -> None:
    settings = config['settings']
    modules = config['modules']

    model_path = settings.get('training', {}).get('model_path', 'models/classifier.pkl')
    predictor = MLPredictor(model_path)
    if predictor.available:
        print(f"ML model loaded from {model_path}")

    repos = {
        k: v for k, v in config['repositories'].items()
        if args.repo is None or v['name'] == args.repo
    }

    if not repos:
        sys.exit(f"No repository found matching '{args.repo}'")

    def process(repo_name, repo_config):
        print(f"Processing: {repo_config['name']}")
        output = run_repo(
            repo_name, repo_config, settings, modules,
            output_format=args.format,
            ai_enabled=args.ai,
            predictor=predictor,
            verbose=args.verbose,
        )
        return repo_name, output

    if len(repos) == 1 or not args.parallel:
        for repo_name, repo_config in repos.items():
            _, output = process(repo_name, repo_config)
            print(f"  -> {output}")
    else:
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(process, k, v): k for k, v in repos.items()
            }
            for future in as_completed(futures):
                try:
                    repo_name, output = future.result()
                    print(f"  {repo_name} -> {output}")
                except Exception as e:
                    print(f"  {futures[future]}: FAILED — {e}")


def cmd_train(args, config: Dict) -> None:
    from training.trainer import train
    settings = config['settings']
    model_path = settings.get('training', {}).get('model_path', 'models/classifier.pkl')
    min_samples = settings.get('training', {}).get('min_training_samples', 20)
    train(args.train, model_path, min_samples)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Find atomic typo candidates in documentation repositories.'
    )
    parser.add_argument(
        '--train', metavar='JSONL',
        help='Train ML classifier from a labeled JSONL file and exit.'
    )
    parser.add_argument(
        '--repo', metavar='NAME',
        help='Run only on the repository with this display name.'
    )
    parser.add_argument(
        '--format', choices=['jsonl', 'csv'], default='jsonl',
        help='Output format (default: jsonl).'
    )
    parser.add_argument(
        '--ai', action='store_true',
        help='Enable AI reviewer for borderline-confidence tokens.'
    )
    parser.add_argument(
        '--parallel', action='store_true',
        help='Process multiple repos concurrently.'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Print per-stage token counts.'
    )

    args = parser.parse_args()
    config = load_config()

    if args.train:
        cmd_train(args, config)
    else:
        cmd_run(args, config)


if __name__ == '__main__':
    main()
