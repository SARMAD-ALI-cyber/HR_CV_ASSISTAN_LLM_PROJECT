from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from cv_assistant.utils.json_schema import CVSchema
from cv_assistant.utils.utils import save_json
from dotenv import load_dotenv
import os

load_dotenv()

LLM=ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    api_key=os.getenv("GOOGLE_API_KEY")
)





def PIPELINE_03_CLEAN_TEXT_PARSER(processes_text:str, cleaning_log:dict):
    parser=JsonOutputParser(pydantic_object=CVSchema)
    prompt=PromptTemplate(
        template="You are a HR CV assistant and you are best at your job, your task is to carefully read applicants' CVs" \
        "and extract the required information from the CVs. You only have to extract the fields mentioned" \
        "in the format instructions and there is a description with examples for each field given to you for your reference.\n{format_instructions}\n{context}\n",
        input_variables=["context"],
        partial_variables={"format_instructions":parser.get_format_instructions()}

    )

    chain=prompt | LLM | parser

    response=chain.invoke({
        "context":processes_text
    })
    output_path=save_json(response,cleaning_log.get("filename"))
    return output_path
