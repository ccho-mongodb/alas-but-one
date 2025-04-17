import re
from typing import Dict
from tasks.base_task import BaseTask
from models.token import Token
from models.token_location import TokenLocation

class TokenizerTask(BaseTask):
    def __init__(self, settings_config, repo_config):
        super().__init__(settings_config, repo_config)
        self.word_regex = re.compile(r'\b(?![_\-0-9])[A-Za-z0-9\']+\b')

    def run(self, content_dict: Dict[str, str]) -> Dict[str, Token]:
        validated_content = self.validate_input(content_dict)
        token_dict = {}

        for key, content in validated_content.items():
            lines = content.lower().split('\n')
            for i, line in enumerate(lines):
                for word in re.findall(self.word_regex, line):
                    if word in token_dict:
                        token = token_dict[word]
                        token.locations.append(TokenLocation(key, i))
                    else:
                        token_dict[word] = Token(word, self.repo_config['name'], [TokenLocation(key, i)])

        return self.validate_output(token_dict)

    def validate_input(self, input_data: Dict[str, str]) -> Dict[str, str]:
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary of file paths and contents")
        return input_data

    def validate_output(self, output_data: Dict[str, Token]) -> Dict[str, Token]:
        if not isinstance(output_data, dict):
            raise TypeError("Output must be a dictionary of tokens")
        return output_data
