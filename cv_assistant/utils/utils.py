import os, json
from pathlib import Path
from datetime import datetime
from typing import Any
from cv_assistant import ENV

JSON_DIR=ENV.JSON_DIR


def list_cv_files(directory: Path):
    dir_path = Path(directory)


    files = [f for f in dir_path.iterdir() if f.suffix.lower() in [".pdf", ".docx"]]

    return files

def save_json(obj: Any, filename: str):
    p:Path=JSON_DIR / f"{filename}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    return str(p)

