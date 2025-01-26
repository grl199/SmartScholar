
'''
Main (executable) script
'''

import os
import argparse
from typing import Any
import logging
import json
import pandas as pd
from typing import Literal
from dotenv import load_dotenv
import streamlit as st



from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END 


from pydantic import BaseModel
from bigquery_manager import BigQueryTableManager
from utilities import extract_pdf_text, read_config,set_logger
import constants

logger = logging.getLogger('default_logger')



def draw_graph(graph):
    '''
    Draw the graph
    '''
    _ = (
        graph
        .get_graph()
        .draw_mermaid_png(output_file_path='../test/resources/simple_graph.png')
    )


class GraphState(BaseModel):
    '''
    Basic configuration for LangGraph
    '''
    graph_state: str
    number_interactions: int = 0
    sections: dict = {}
    pdf_file: Any
    raw_text: str
    raw_sections: str
    bq_manager: BigQueryTableManager

    class Config:
        '''
        Allow arbitrary types (e.g. BigQueryTableManager)
        '''
        arbitrary_types_allowed = True



# Extract raw text

def extract_raw_text(state):
    '''
    Node for extracting raw text from pdf
    '''
    logger.info("Get plain text from given pdf")

    state.number_interactions += 1
    state.raw_text = extract_pdf_text(state.pdf_file)
    logger.info("Text extracted successfully")
    st.write(f'Text extracted successfully. First 50 words: {state.raw_text[:50]}')
    return state

# Define node to extract sections


def extract_sections(state):
    '''
    Node to extract sections. Ideally, we would use a LLM to extract the sections, defined as a global variable below.
    '''

    logger.info('Extract the key components of the paper: Title, Abstract, Authors, Publication_date, Methodology, Results and Conclusions')
    state.number_interactions += 1

    default_output = '{\
                "title": "The Impact of Digital Technologies on Educational Accessibility",\
                "abstract" : "This paper explores the impact of digital technologies on educational accessibility",\
                "publication_date": "2021-01-01",\
                "journal": "Journal of Digital Education",\
                "authors": ["Maria Gonzalez", "John Smith"],\
                "summary" : "Example of summary",\
                "keywords": ["Digital", "Education", "Technology"]}'

    if MODEL == 'TEST': #Test mode will return standard output
        logger.info('Test mode (no llm): Default output:')
        st.write('Test mode: Default output:')
        state.raw_sections = default_output
    else:
        prompt = f'Extract the following key components of the paper: {str(json.loads(default_output).keys())}.\
                Return only the result in a json format with these components as keys. The paper is given as follows:{state.raw_text}.\
                An example of the expected output is: {default_output}.'


        state.raw_sections = MODEL.invoke(prompt).content
        logger.info('Raw output from LLM: %s', state.raw_sections)
    
    state.sections = json.loads(state.raw_sections)

    return state


def check_llm_output(state)-> Literal["extract_sections", 'load_row_big_query']:
    '''
    Node defined to check if the output of the LLM is correct (i.e. a json object with the given keys)
    '''
    logger.info("Handle LLM output")

    state.number_interactions += 1
    # Check if json is returned
    try:
        json_object = json.loads(state.raw_sections)
        
        #We can add more checks here to ensure that the json object is correct

        assert json_object.keys() == {'title', 'abstract', 'publication_date', 'journal', 'authors', 'summary', 'keywords'}

        logger.info("Sections extracted succcessfully")

        st.write('Following extracted sections are to be loaded into a BigQuery table:')
        st.table(pd.DataFrame(list(state.sections.items()), columns=['Section', 'Value']))

    
        return 'load_row_big_query'


    except ValueError as e:
        logger.error("%s: Output is not correct.", str(e))
        st.write('Output is not correct. Please try again.')
        return 'extract_sections'  # Returns to llm node to try again
    

def load_row_big_query(state):
    '''
    Node to load the extracted sections into BigQuery
    '''

    logger.info('Load the extracted sections into BigQuery')
    state.number_interactions += 1

    state.bq_manager.add_row(state.sections)

    return state


def main(config = read_config('config.yaml'),
         pdf_file:str = None,
         draw:bool = False,
         logger = logging.getLogger('main')):
    '''
    Main method
    '''
    
    global MODEL
    if config['inputs'].get('llm_model',constants.DEFAULT_LLM_MODEL) == 'TEST':
        MODEL = 'TEST'
    else:
        MODEL =  ChatOpenAI(model=config['inputs'].get('llm_model',constants.DEFAULT_LLM_MODEL),
                            temperature=config['inputs'].get('temperature',constants.DEFAULT_TEMPERATURE))


    logger.info("Processing file: %s", pdf_file)


    #Client BigQuery
    
    logger.info('Initializing BigQuery client...')
    bq_manager = BigQueryTableManager(config = config)

    #Create table if not exits

    bq_manager.setup_bq_table()

    graph = StateGraph(GraphState)
    graph.add_node('extract_raw_text' , extract_raw_text)
    graph.add_node('extract_sections' , extract_sections)
    graph.add_node('load_row_big_query' , load_row_big_query)

    graph.add_edge(START, "extract_raw_text")
    graph.add_edge("extract_raw_text", "extract_sections")
    graph.add_conditional_edges("extract_sections", check_llm_output)
    graph.add_edge("extract_sections", "load_row_big_query")
    graph.add_edge("load_row_big_query", END)

    graph_compiled = graph.compile()

    if draw:
        draw_graph(graph_compiled)


    base_dict = {"graph_state": "",
                "number_interactions": 0,
                "raw_sections": "",
                'sections':{} ,
                'pdf_file': pdf_file,
                'raw_text':'',
                'bq_manager': bq_manager}
    

    graph_compiled.invoke(base_dict)
    logger.info("Success!")
    
    
def setup_st_page():
    '''
    Set up the streamlit page
    '''

    st.set_page_config(
        page_title="SmartScholar",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed",
    )



if __name__ == '__main__':

    setup_st_page()

    st.title("SmartScholar - Academic paper file processor")
    st.write("Upload a PDF file to process its content.")

    parser = argparse.ArgumentParser(description="This script accepts arguments.")
    parser.add_argument("--conf",type=str, default="config.yaml", help="config file")
    parser.add_argument("--pdf",type=str, help="pdf file to process")

    # Parse the arguments from the command line
    args = parser.parse_args()
    assert 'conf' in args, "Please provide a config file"
    
    config = read_config(args.conf)
    logger = set_logger(config = config)


    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        main(config = config, pdf_file=uploaded_file)