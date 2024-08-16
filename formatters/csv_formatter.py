import csv
from typing import List, Dict
from tasks.base_task import BaseTask
from models.token import Token

class CsvFormatterTask(BaseTask):
    def __init__(self, settings_config, repo_config):
        super().__init__(settings_config, repo_config)
        self.field_names = ['word', 'repo', 'locations', 'num_occurrences', 'misspelled', 'ignore']

    def run(self, tokens: Dict[str, Token]) -> str:
        validated_tokens = self.validate_input(tokens)

        output_file = f"{self.repo_config['name']}.csv"

        with open(output_file, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.field_names)
            writer.writeheader()

            for token in validated_tokens.values():
                writer.writerow({
                    'word': token.text,
                    'repo': token.repo,
                    'locations': self.format_locations(token.locations),
                    'num_occurrences': len(token.locations),
                    'misspelled': token.misspelled,
                    'ignore': token.ignore
                })

        return self.validate_output(output_file)

    def format_locations(self, token_locations):
        if len(token_locations) == 1:
            return f"{token_locations[0].filename}:{token_locations[0].line}".rstrip()
        else:
            return "\n".join([f"{loc.filename}:{loc.line}" for loc in token_locations])

    def validate_input(self, input_data: Dict[str, Token]) -> Dict[str, Token]:
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary of tokens")
        return input_data

    def validate_output(self, output_data: str) -> str:
        if not isinstance(output_data, str):
            raise TypeError("Output must be a string (file path)")
        return output_data
