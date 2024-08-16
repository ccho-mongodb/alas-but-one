from typing import List, Dict, Any
from tasks.factory import TaskFactory

class Pipeline:
    def __init__(self, settings_config: Dict[str, Any], repo_config: Dict[str, Any], modules_config: Dict[str, Any]):
        self.settings_config = settings_config
        self.repo_config = repo_config
        self.modules_config = modules_config 
        self.tasks = []

    def add_task(self, task_name: str):
        task = TaskFactory.create_task(task_name, self.settings_config, self.repo_config, self.modules_config)
        self.tasks.append(task)

    def run(self, initial_input: Any):
        result = initial_input
        for task in self.tasks:
            result = task.run(result)

        return result

