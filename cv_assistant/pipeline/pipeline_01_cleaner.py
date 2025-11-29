from langchain_community.document_loaders import (
    PyMuPDFLoader, 
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,)
from langdetect import detect
import re
from pathlib import Path
from typing import List
import pprint
import hashlib
'''This file takes care of basic cleaning
1) Zero text files
2) Unsupported files
3) Unsupported language
4) Maintains cleaning log
5) Checks for scanned docs and use OCR to extract text
6) Handels duplicate files using SHA256
7) Normalize white spaces
8) Removes \t
9) Removes \n
10) Removes Null bytes
11) Encodes text to standard form utf8
12) Collapse multiple white spaces'''

def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def _get_logger():
    return {
        "filename": "",
        "file_type": "",
        "hash": "",
        "ocr_used": False,
        "zero_text": False,
        "language": None,
        "issue": [],
        "has_issue":False
    }
def _file_type(file_path:Path):
    '''File type checker currently only accepts
    pdfs and docx'''
    extension=file_path.suffix.lower()
    if extension==".pdf":
        return "pdf"
    elif extension==".docx":
        return "docx"
    

def _clean_text(text: str) -> str:
    """
    Light cleaning — no aggressive formatting removal,
    because we NEED headings and layout clues.
    """
    
    text = text.replace("\x00", "")
    text = text.encode("utf-8", "ignore").decode()
    text=text.replace("\t","")
    text = re.sub(r"\s+\n", "\n", text)  
    text = re.sub(r"\n{3,}", "\n\n", text) 
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def PIPELINE_01_PDFLOADER(file_path:Path):
    file_type=_file_type(file_path=file_path)
    CLEANING_LOGGER=_get_logger()



    '''If it's a pdf'''
    if file_type=="pdf":
        try:
            raw_text=PyMuPDFLoader(file_path).load()
            clean_text=_clean_text(raw_text[0].page_content)
            '''Logging'''
            CLEANING_LOGGER["ocr_used"]=False
            CLEANING_LOGGER["filename"]=file_path.stem
            CLEANING_LOGGER["file_type"]=file_type
            CLEANING_LOGGER["language"]=detect(clean_text) if clean_text.strip() else "unknown"
            CLEANING_LOGGER["hash"]=_hash_file(file_path)
            if CLEANING_LOGGER["language"]=="unknown":
                CLEANING_LOGGER["has_issue"]=True
                CLEANING_LOGGER["issue"].append("Unknown language")
            if len(clean_text.strip())==0:
                CLEANING_LOGGER["zero_text"]=True
                CLEANING_LOGGER["has_issue"]=True
                CLEANING_LOGGER["issue"].append("Zero text")
            
        except Exception:
            '''Handels scanned pdfs here, OCR'''
            raw_text=UnstructuredPDFLoader(
                file_path,
                strategy="ocr_only"
            ).load()
            clean_text=_clean_text(raw_text[0].page_content)
            '''Logging'''
            CLEANING_LOGGER["ocr_used"]=True
            CLEANING_LOGGER["filename"]=file_path.name
            CLEANING_LOGGER["file_type"]=file_type
            CLEANING_LOGGER["language"]=detect(clean_text) if clean_text.strip() else "unknown"
            CLEANING_LOGGER["hash"]=_hash_file(file_path)
            if CLEANING_LOGGER["language"]=="unknown":
                CLEANING_LOGGER["has_issue"]=True
                CLEANING_LOGGER["issue"].append("Unknown language")
            if len(clean_text.strip())==0:
                CLEANING_LOGGER["zero_text"]=True
                CLEANING_LOGGER["has_issue"]=True
                CLEANING_LOGGER["issue"].append("Zero text")
        return clean_text,raw_text[0].metadata,CLEANING_LOGGER
    
        '''If it's a docx'''
    elif file_type=="docx":
        raw_text=UnstructuredWordDocumentLoader(file_path=file_path).load()
        clean_text=_clean_text(raw_text[0].page_content)
        CLEANING_LOGGER["ocr_used"]=False
        CLEANING_LOGGER["filename"]=file_path.name
        CLEANING_LOGGER["file_type"]=file_type
        CLEANING_LOGGER["language"]=detect(clean_text) if clean_text.strip() else "unknown"
        CLEANING_LOGGER["hash"]=_hash_file(file_path)
        if CLEANING_LOGGER["language"]=="unknown":
            CLEANING_LOGGER["has_issue"]=True
            CLEANING_LOGGER["issue"].append("Unknown language")
        if len(clean_text.strip())==0:
            CLEANING_LOGGER["zero_text"]=True
            CLEANING_LOGGER["has_issue"]=True
            CLEANING_LOGGER["issue"].append("Zero text")
        return clean_text,raw_text[0].metadata, CLEANING_LOGGER
    




if __name__=="__main__":
    text,metadata,loggs=PIPELINE_01_PDFLOADER(Path(".\\data\\raw\\AHMAD_SARMAD_ALI_CV.pdf"))
    pprint.pp(text)
    print(loggs)