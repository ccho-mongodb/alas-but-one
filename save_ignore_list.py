import os, json, re, collections, csv
from pymongo import MongoClient, UpdateOne

def get_ignore_lists_and_collection():
    connection_uri = os.environ['ABO_MONGO_URI']

    with open('config.json') as f:
        config = json.load(f)

    dbName = config['ignore_list']['database']
    collName = config['ignore_list']['collection']

    coll = MongoClient(connection_uri)[dbName][collName]

    ignore_dict = {}
    results = coll.find()
    for result in results:
        ignore_dict[result['repo_name']] = result['words']

    return ignore_dict, coll

def main():

    csv_file = 'out.csv'

    update_dict = collections.defaultdict(set)

    with open(csv_file) as file:
        reader = csv.DictReader(file)

        for row in reader:
            ignore_val = row['ignore']
            if ignore_val is not None:
                if re.search('[yY]', ignore_val):
                    word_tuple = tuple((row['word'].lower(), 1))
                    update_dict[row['repo']].add(word_tuple)
                elif re.search('[nN]', ignore_val):
                    word_tuple = tuple((row['word'].lower(), 0))
                    update_dict[row['repo']].add(word_tuple)

    if len(update_dict) > 0:
        add_words = []
        remove_words = []

        for repo_name, updates in update_dict.items():
            for update in updates:
                add_words = [ x[0] for x in updates if x[1] == 1 ]
                remove_words = [ x[0] for x in updates if x[1] == 0 ]

        ignore_dict, ignore_coll = get_ignore_lists_and_collection()
        update_ops = []
        for repo_name, update_tuple in update_dict.items():
            if len(add_words) > 0:
                update_ops.append(UpdateOne({ 'repo_name': repo_name }, { '$addToSet': {'words': { '$each': add_words }}}, upsert=True ))
            if len(remove_words) > 0:
                update_ops.append(UpdateOne({ 'repo_name': repo_name }, { '$pullAll': {'words': remove_words }} ))

        if len(update_ops) > 1:
            ignore_coll.bulk_write(update_ops)

if __name__ == "__main__":
    main()
