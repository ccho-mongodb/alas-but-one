from typing import Dict, Any
import importlib
from tasks.base_task import BaseTask

class TaskFactory:

    @staticmethod
    def create_task(name: str, settings_config: Dict[str, Any], repo_config: Dict[str, Any], modules_config: Dict[str, Any]) -> BaseTask:
        task_config = modules_config[name]
        module = importlib.import_module(task_config['path'])
        task_class = getattr(module, task_config['className'])

        return task_class(settings_config, repo_config)
