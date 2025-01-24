'''
Script to test utilities.py (miscellaneous functions)
'''

from src.utilities import extract_pdf_text, read_config, set_logger


def test_extract_pdf_text(sample_pdf_file,logger):
    '''
    Test extract_pdf_text function
    '''

    text = extract_pdf_text(sample_pdf_file)
    
    logger.info(f"Extracted text: {text[:50]}")

def test_read_config():
    '''
    Test read_config function
    '''
    config=read_config(file = 'config.yaml')
    assert 'inputs' in config

def test_set_logger(config, logger):
    '''
    Test set_logger function
    '''
    set_logger(config = config)
    logger.info('Logger set up correctly')