from typing import Dict
from tasks.base_task import BaseTask
from models.token import Token
from pymongo import MongoClient

class IgnoreListTask(BaseTask):
    def run(self, token_dict: Dict[str, Token]) -> Dict[str, Token]:
        validated_tokens = self.validate_input(token_dict)
        
        client = MongoClient(self.settings_config['MONGODB_URI'])
        db_name = self.settings_config['ignore_list']['database']
        coll_name = self.settings_config['ignore_list']['collection']
        
        coll = client[db_name][coll_name]
        result = coll.find_one({'repo_name': self.repo_config['name']})

        if result and 'words' in result:
            ignore_list = result['words']
            for word in ignore_list:
                if word in validated_tokens:
                    validated_tokens[word].ignore = 'Y'

        return self.validate_output(validated_tokens)

    def validate_input(self, input_data: Dict[str, Token]) -> Dict[str, Token]:
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary of tokens")
        return input_data

    def validate_output(self, output_data: Dict[str, Token]) -> Dict[str, Token]:
        if not isinstance(output_data, dict):
            raise TypeError("Output must be a dictionary of tokens")
        return output_data
