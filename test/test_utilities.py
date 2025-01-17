import unittest
from utilities import extract_pdf_text

import logging
logger = logging.getLogger('test_utilities')

def test_extract_pdf_text(sample_pdf_file):
    # Assuming you have a sample PDF file for testing

    text = extract_pdf_text(sample_pdf_file)
    
    logger.info(f"Extracted text: {text[:50]}")
