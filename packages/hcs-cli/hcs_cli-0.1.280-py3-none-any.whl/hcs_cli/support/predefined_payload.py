import os.path as path


def load(name: str) -> str:
    file_name = path.join(path.dirname(__file__), f"../payload/{name}")
    file_name = path.abspath(file_name)
    with open(file_name, "rt") as f:
        return f.read()
