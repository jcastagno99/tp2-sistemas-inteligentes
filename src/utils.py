import os, yaml

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def project_path(*parts):
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), *parts))
