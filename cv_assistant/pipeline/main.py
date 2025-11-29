from cv_assistant.pipeline.pipeline_01_cleaner import PIPELINE_01_PDFLOADER
from cv_assistant.pipeline.pipeline_02_handling_cleaner import PIPELINE_02_HANDLING_CLEANER
from cv_assistant.pipeline.pipeline_03_clean_text_parser import PIPELINE_03_CLEAN_TEXT_PARSER
from cv_assistant.pipeline.pipeline_04_scoring import PIPELINE_04_SCORING
from cv_assistant.utils.status import get_progress_bar
from cv_assistant.utils.utils import list_cv_files
from cv_assistant.utils.logger import(
    warn,
    info,
    error,
    success,
)
from pathlib import Path
from rich.progress import (
    Progress,
    TimeElapsedColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from cv_assistant import ENV
import pprint
__SEEN_HASHES__={}

'''Get CVs from folder'''
cvs_list=list_cv_files(ENV.RAW_DATA_DIR)


with get_progress_bar() as progress:
    cleaning_task=progress.add_task(
        description=f"[red]Found {len(cvs_list)} documents to clean..."
    )

    for cv in cvs_list:
        clean_text,metadata,cleaning_log=PIPELINE_01_PDFLOADER(Path(cv))

        '''Handling duplicates here'''
        if cleaning_log["hash"] not in __SEEN_HASHES__:
            __SEEN_HASHES__[cleaning_log.get("filename")]=cleaning_log.get("hash")
        else:
            warn(f"File {cleaning_log.get("filename")} with HASH {cleaning_log.get("hash")} is duplicate skipping it.....")
            cleaning_log["has_issue"]=True
            cleaning_log["issue"].append("Duplicate file")
            PIPELINE_02_HANDLING_CLEANER(cleaning_log=cleaning_log)
            progress.update(cleaning_task,advance=1)
            continue

        PIPELINE_02_HANDLING_CLEANER(cleaning_log=cleaning_log)
        if cleaning_log["has_issue"]==True:
            progress.update(cleaning_task,advance=1)
            continue

        output_path=PIPELINE_03_CLEAN_TEXT_PARSER(processes_text=clean_text,cleaning_log=cleaning_log)
        success(f"Succesfully saved the JSON for {cleaning_log["filename"]} at {output_path}")

        progress.update(cleaning_task,advance=1)
'''Calculating scores'''

all_scores=PIPELINE_04_SCORING()
info(f"Successfully scored {len(all_scores)} CVs")
