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
    SCORED_CV_DIR:Path=OUTPUT_DIR / "scored_cvs"
    CONFIG_DIR: Path= ROOT_DIR / "cv_assistant" / "config"
    MAPPINGS_DIR:Path=ROOT_DIR / "cv_assistant" / "mappings"
    RANKING_DIR: Path=DATA_DIR / 'rankings'
    EXPANATIONS_DIR:Path=RANKING_DIR / "explanations"
    ANNOTATIONS_DIR:Path=DATA_DIR / "annotations"
    EVALUATION_DIR:Path=DATA_DIR / "evaluation"
    ABLATION_CONFIGS_DIR:Path=ROOT_DIR / "cv_assistant" / "experiments" / "ablation_configs"
    ABLATIONS_DIR:Path=OUTPUT_DIR / "ablations"

ENV.DATA_DIR.mkdir(exist_ok=True, parents=True)
ENV.RAW_DATA_DIR.mkdir(exist_ok=True, parents=True)
ENV.PROCESSING_LOGS_DIR.mkdir(exist_ok=True, parents=True)
ENV.OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
ENV.JSON_DIR.mkdir(exist_ok=True, parents=True)
ENV.CONFIG_DIR.mkdir(exist_ok=True, parents=True)
ENV.MAPPINGS_DIR.mkdir(exist_ok=True, parents=True)
ENV.SCORED_CV_DIR.mkdir(exist_ok=True, parents=True)
ENV.RANKING_DIR.mkdir(exist_ok=True, parents=True)
ENV.EXPANATIONS_DIR.mkdir(exist_ok=True, parents=True)
ENV.ANNOTATIONS_DIR.mkdir(exist_ok=True, parents=True)
ENV.EVALUATION_DIR.mkdir(exist_ok=True, parents=True)
ENV.ABLATIONS_DIR.mkdir(exist_ok=True, parents=True)
ENV.ABLATION_CONFIGS_DIR.mkdir(exist_ok=True, parents=True)
