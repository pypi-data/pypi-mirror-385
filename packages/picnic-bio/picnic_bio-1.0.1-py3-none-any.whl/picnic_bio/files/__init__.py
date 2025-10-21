import os
from pathlib import Path

dir_name = os.path.dirname(__file__)


def get_model_dir_path() -> Path:
    dir_name_path = Path(dir_name)
    return dir_name_path / "models_llps"


def get_go_dir_path() -> Path:
    dir_name_path = Path(dir_name)
    return dir_name_path / "go"
