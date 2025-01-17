
import os
#os.chdir('src')


import logging
logging.basicConfig(
    level=logging.INFO,  # Cambia a INFO, WARNING, etc., según lo necesario
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger('main')

from dotenv import load_dotenv
import argparse


from langgraph.graph import StateGraph
from langchain.llms import HuggingFaceHub #type:ignore
from langgraph.graph import START, END 
import PyPDF2
from pydantic import BaseModel
from bigquery_manager import BigQueryTableManager


from utilities import extract_pdf_text
import constants

from lang_graph_manager import *


if __name__ == '__main__':
    
    graph = StateGraph(GraphState)

    graph.add_node('extract_raw_text' , extract_raw_text)
    graph.add_node('extract_sections' , extract_sections)
    graph.add_node('load_row_big_query' , extract_sections)

    graph.add_edge(START, "extract_raw_text")
    graph.add_edge("extract_raw_text", "extract_sections")
    graph.add_conditional_edges("extract_sections", check_llm_output)
    graph.add_edge("extract_sections", "load_row_big_query")
    graph.add_edge("load_row_big_query", END)

    graph_compiled = graph.compile()

    parser = argparse.ArgumentParser(description="This script accepts arguments.")
    parser.add_argument("--pdf_file",type=str, help="pdf file to process")

    # Parse the arguments from the command line
    args = parser.parse_args()

    if not args.pdf_file:
        args.pdf_file = '/Users/guille/Desktop/ProyectosML/Astrafy/tests/resources/impact_of_digitalization_education.pdf'

    _ = (
        graph_compiled
        .get_graph()
        .draw_mermaid_png(output_file_path='/Users/guille/Desktop/ProyectosML/Astrafy/simple_graph.png')
    )

    base_dict = {"graph_state": "",
                "number_interactions": 0,
                "raw_sections": "",
                'sections':{} ,
                'pdf_file': args.pdf_file,
                'raw_text':'',
                'bq_manager': BigQueryTableManager()}
    

    resp = graph_compiled.invoke(base_dict)

    logger.info(f"Output: {resp['sections']}")