from __future__ import annotations
from pathlib import Path

_root_path=Path(__file__).parent.parent.resolve()




class ENV:
    ROOT_DIR: Path=_root_path
    DATA_DIR: Path=ROOT_DIR / "data"
    RAW_DATA_DIR: Path= DATA_DIR / "raw"
    PROCESSING_LOGS_DIR: Path=DATA_DIR / "processing_logs"
    OUTPUT_DIR:Path=DATA_DIR / "outputs"
    JSON_DIR: Path=OUTPUT_DIR / "extracted_jsons"


ENV.DATA_DIR.mkdir(exist_ok=True, parents=True)
ENV.RAW_DATA_DIR.mkdir(exist_ok=True, parents=True)
ENV.PROCESSING_LOGS_DIR.mkdir(exist_ok=True, parents=True)
ENV.OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
ENV.JSON_DIR.mkdir(exist_ok=True, parents=True)
