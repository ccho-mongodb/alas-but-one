"""
Persist ignore-list changes from a reviewed CSV or JSONL output file to MongoDB.

Usage:
  python save_ignore_list.py output.jsonl
  python save_ignore_list.py output.csv

For JSONL: set "ignore": true/false on each record.
For CSV:   set the 'ignore' column to 'Y'/'N'.

Requires ABO_MONGO_URI environment variable.
"""
import collections
import csv
import json
import os
import re
import sys
from pymongo import MongoClient, UpdateOne


def _get_collection():
    uri = os.environ.get('ABO_MONGO_URI')
    if not uri:
        sys.exit("ABO_MONGO_URI environment variable is not set.")

    with open('config.json') as f:
        config = json.load(f)

    db_name = config['settings']['ignore_list']['database']
    coll_name = config['settings']['ignore_list']['collection']
    return MongoClient(uri)[db_name][coll_name]


def _load_csv(path: str) -> dict:
    """Returns {repo_name: {word: ignore_bool}}"""
    update_dict = collections.defaultdict(dict)
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ignore_val = row.get('ignore', '')
            word = row.get('word', '').lower()
            repo = row.get('repo', '')
            if not word or not repo:
                continue
            if re.search(r'[yY]', ignore_val):
                update_dict[repo][word] = True
            elif re.search(r'[nN]', ignore_val):
                update_dict[repo][word] = False
    return update_dict


def _load_jsonl(path: str) -> dict:
    """Returns {repo_name: {word: ignore_bool}}"""
    update_dict = collections.defaultdict(dict)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            word = record.get('word', '').lower()
            repo = record.get('repo', '')
            ignore = record.get('ignore')
            if not word or not repo or ignore is None:
                continue
            update_dict[repo][word] = bool(ignore)
    return update_dict


def _apply_updates(update_dict: dict) -> None:
    if not update_dict:
        print("No updates to apply.")
        return

    coll = _get_collection()
    ops = []

    for repo_name, word_map in update_dict.items():
        add_words = [w for w, v in word_map.items() if v]
        remove_words = [w for w, v in word_map.items() if not v]

        if add_words:
            ops.append(UpdateOne(
                {'repo_name': repo_name},
                {'$addToSet': {'words': {'$each': add_words}}},
                upsert=True,
            ))
        if remove_words:
            ops.append(UpdateOne(
                {'repo_name': repo_name},
                {'$pullAll': {'words': remove_words}},
            ))

    if ops:
        result = coll.bulk_write(ops)
        print(
            f"Applied {len(ops)} operations "
            f"({result.upserted_count} upserted, {result.modified_count} modified)."
        )
    else:
        print("No changes to write.")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python save_ignore_list.py <output.jsonl|output.csv>")

    input_file = sys.argv[1]

    if input_file.endswith('.jsonl'):
        update_dict = _load_jsonl(input_file)
    elif input_file.endswith('.csv'):
        update_dict = _load_csv(input_file)
    else:
        sys.exit("Input file must be .jsonl or .csv")

    _apply_updates(update_dict)


if __name__ == '__main__':
    main()
