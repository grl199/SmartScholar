import os
#os.chdir('src')
import logging
logger = logging.getLogger('lang_graph_manager')

from typing import Literal
import json
from dotenv import load_dotenv
import argparse


from langgraph.graph import StateGraph
from langchain.llms import HuggingFaceHub #type:ignore
from langgraph.graph import START, END 
import PyPDF2
from pydantic import BaseModel


from utilities import extract_pdf_text
from bigquery_manager import BigQueryTableManager
import constants

os.environ['HUGGINGFACEHUB_API_TOKEN'] = os.getenv('HUGGINGFACEHUB_API_TOKEN',constants.DEFAULT_API_KEY)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS',constants.DEFAULT_API_KEY)

MODEL =  HuggingFaceHub(repo_id=constants.DEFAULT_LLM_MODEL,
                         model_kwargs={"temperature": constants.DEFAULT_TEMPERATURE})


class GraphState(BaseModel):
    graph_state: str
    number_interactions: int = 0
    verbose: bool = True
    sections: dict = {}
    pdf_file: str
    raw_text: str
    raw_sections: str
    bq_manager: BigQueryTableManager

    class Config:
        arbitrary_types_allowed = True




# Extract raw text

def extract_raw_text(state):
    if state.verbose:
        logger.info("Get plain text from given pdf")

    state.number_interactions += 1
    state.raw_text = extract_pdf_text(state.pdf_file)
    return state

# Define node to extract sections


def extract_sections(state):

    if state.verbose:
        logger.info('Extract the key components of the paper: Title, Abstract, Authors, Publication_date, Methodology, Results and Conclusions')
    state.number_interactions += 1

    prompt = f'Extract the following key components of the paper: title, abstract, authors,\
             publication_date, journal, methodology and conclusions. Return only the result in a json\
             format with these components as keys. The paper is given as follows:     {state.raw_text}'


    #state.raw_sections = model.invoke(prompt)
    state.raw_sections = '{\
            "title": "The Impact of Digital Technologies on Educational Accessibility",\
            "abstract" : "This paper explores the impact of digital technologies on educational accessibility",\
            "publication_date": "2021-01-01",\
            "journal": "Journal of Digital Education",\
            "authors": ["Maria Gonzalez", "John Smith"],\
            "summary" : "Example of summary",\
            "keywords": ["Digital", "Education", "Technology"]}'
    
    state.sections = json.loads(state.raw_sections)

    return state



def check_llm_output(state)-> Literal["extract_sections", 'load_row_big_query']:
    if state.verbose:
        logger.info("Handle LLM output")

    state.number_interactions += 1
    # Check if json is returned
    try:
        json_object = json.loads(state.raw_sections)
        
        #We can add more checks here to ensure that the json object is correct

        assert json_object.keys() == {'title', 'abstract', 'publication_date', 'journal', 'authors', 'summary', 'keywords'}

        logger.info("Sections extracted successfully")
        
        return 'load_row_big_query'

    except ValueError as e:
        logger.error(f"{str(e)}: Output is not correct.")
        return 'extract_sections'  # Returns to llm node to try again
    

def load_row_big_query(state):

    if state.verbose:
        logger.info('Load the extracted sections into BigQuery')
    state.number_interactions += 1

    state.bq_manager.add_row(state.sections)

    return state

