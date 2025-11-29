import json
from pathlib import Path
from cv_assistant import ENV
from cv_assistant.utils.logger import error

'''This files saves the logging results for corrupted/problamatic files
and all files into a JSONL file. This will help us in future to display these results 
on our UI as JSON is a universal format for frontend, So I think this will work.'''
__LOGS_DIR__=ENV.PROCESSING_LOGS_DIR

ALL_LOGS=__LOGS_DIR__ / "cleaning_logs.jsonl"
ERROR_LOGS=__LOGS_DIR__ / "error_logs.jsonl"



def PIPELINE_02_HANDLING_CLEANER(cleaning_log:dict):

    with ALL_LOGS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(cleaning_log, ensure_ascii=False) + "\n")

    if cleaning_log.get("has_issue", False):
        error(f"File {cleaning_log["filename"]} has issues logging into the error_logs.jsonl and skippin it....")
        with ERROR_LOGS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(cleaning_log, ensure_ascii=False) + "\n")


