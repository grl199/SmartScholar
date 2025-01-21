import PyPDF2
import yaml
import logging


def extract_pdf_text(pdf_path):
    '''
    Function used to extract raw text from a pdf
    '''
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def read_config(file):
    '''
    Read the config file
    '''
    with open(file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def set_logger(config = None):
    '''
    Set the logger
    '''
    
    logging.basicConfig(
        level = config.get('log_level', 'INFO'),
        format= config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    logger = logging.getLogger('main')

    return logger