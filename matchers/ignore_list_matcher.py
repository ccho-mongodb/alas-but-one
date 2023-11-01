import os, json, re, collections, csv
from pymongo import MongoClient

def run(token_dict, repo, dbName, collName):
    connection_uri = os.environ['ABO_MONGO_URI']

    coll = MongoClient(connection_uri)[dbName][collName]
    result = coll.find_one({ 'repo_name': repo })

    if result:
        ignore_list = result['ignore']

        for word in ignore_list['words']:
            if word in token_dict:
                token_dict[word].ignore = 'Y'

