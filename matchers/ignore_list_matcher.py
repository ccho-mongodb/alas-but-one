import os, json, re, collections, csv
from pymongo import MongoClient

def run(token_dict, repo, connection_uri, dbName, collName):

    client = MongoClient(connection_uri)

    coll = client[dbName][collName]
    result = coll.find_one({ 'repo_name': repo })

    if result:
        ignore_list = result['ignore']

        for word in ignore_list['words']:
            if word in token_dict:
                token_dict[word].ignore = 'Y'

