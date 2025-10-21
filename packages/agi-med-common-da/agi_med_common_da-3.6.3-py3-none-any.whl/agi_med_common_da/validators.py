import os
import re
from pathlib import Path


def is_file_exist(filepath: str | os.PathLike[str] | Path) -> str | os.PathLike | Path:
    if not os.path.exists(filepath):
        raise ValueError(f"File {filepath} is not exist. Check the path")
    return filepath


def validate_prompt(prompt: str, prompt_required_keys: set[str]) -> str:
    exist_keys: set[str] = set(re.findall(r"{(.*?)}", prompt))
    if missed_keys := prompt_required_keys.difference(exist_keys):
        raise ValueError(f"Missing required key in prompt: {missed_keys}")
    if extern_keys := exist_keys.difference(prompt_required_keys):
        raise ValueError(f"You have more keys for prompt: {extern_keys}")
    return prompt
