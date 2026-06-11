from typing import Any, Callable, Dict, List


class HookRegistry:
    """
    Manages named pre/post pipeline hooks.

    Usage:
        hooks = HookRegistry()

        @hooks.pre_repo
        def log_start(repo_name, config):
            print(f"Starting {repo_name}")

        @hooks.post_stage('spell_checker')
        def after_spell(stage_name, data):
            print(f"{len(data)} tokens after spell check")
            return data  # must return data
    """

    def __init__(self):
        self._pre_repo: List[Callable] = []
        self._post_repo: List[Callable] = []
        self._pre_stage: Dict[str, List[Callable]] = {}
        self._post_stage: Dict[str, List[Callable]] = {}

    def pre_repo(self, fn: Callable) -> Callable:
        self._pre_repo.append(fn)
        return fn

    def post_repo(self, fn: Callable) -> Callable:
        self._post_repo.append(fn)
        return fn

    def pre_stage(self, stage_name: str) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self._pre_stage.setdefault(stage_name, []).append(fn)
            return fn
        return decorator

    def post_stage(self, stage_name: str) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self._post_stage.setdefault(stage_name, []).append(fn)
            return fn
        return decorator

    def fire_pre_repo(self, repo_name: str, config: Dict) -> None:
        for fn in self._pre_repo:
            fn(repo_name, config)

    def fire_post_repo(self, repo_name: str, result: Any, config: Dict) -> None:
        for fn in self._post_repo:
            fn(repo_name, result, config)

    def fire_pre_stage(self, stage_name: str, data: Any) -> Any:
        for fn in self._pre_stage.get(stage_name, []):
            data = fn(stage_name, data)
        return data

    def fire_post_stage(self, stage_name: str, data: Any) -> Any:
        for fn in self._post_stage.get(stage_name, []):
            data = fn(stage_name, data)
        return data


default_hooks = HookRegistry()
