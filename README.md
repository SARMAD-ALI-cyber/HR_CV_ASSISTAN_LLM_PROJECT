# HR_CV_ASSISTAN_LLM_PROJECT

A resume/CV parsing and analysis tool powered by Large Language Models.

## Features

- Automated CV/Resume parsing
- Text extraction from multiple document formats
- Structured data extraction using LLMs
- Pipeline-based processing architecture

## Prerequisites

- Python 3.12 or higher
- pip

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SARMAD-ALI-cyber/HR_CV_ASSISTAN_LLM_PROJECT.git
cd HR_CV_ASSISTAN_LLM_PROJECT
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv llm_proj

# Activate virtual environment
# Windows
llm_proj\Scripts\activate

# Linux/Mac
source llm_proj/bin/activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

This will install all required packages listed in `setup.py`.

### 4. Verify Installation

```powershell
# Check if package is installed
pip show cv-assistant

# Test import
python -c "import cv_assistant; print('✓ Installation successful!')"
```

Expected output:
```
✓ Installation successful!
```

## Configuration

Create a `.env` file in the project root with your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
```


## Project Structure

```
Code/
├── cv_assistant/
│   ├── __init__.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── pipeline_01_cleaner.py
│   │   ├── pipeline_02_handling_cleaner.py
│   │   └── pipeline_03_clean_text_parser.py
│   └── utils/
│       ├── __init__.py
│       ├── json_schema.py
│       ├── status.py
│       └── utils.py
├── data/
│   ├── outputs/
│   ├── processing_logs/
│   └── raw/
├── llm_proj/          (virtual environment directory)
├── notebooks/
├── .env
├── requirements.txt
├── setup.py
└── PROJECT_SETUP.md   (this file)
```

---

## Author

Ahmad Sarmad Ali
