from pathlib import Path


def folder_create(path):
    Path(path).mkdir(parents=True, exist_ok=True)
