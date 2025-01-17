import pytest
import os
from unittest.mock import patch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import logging
logging.basicConfig(
    level=logging.INFO,  # Cambia a INFO, WARNING, etc., según lo necesario
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger('conftest')


@pytest.fixture(scope='session', autouse=True)
def set_google_credentials():
    """
    Fixture to set the GOOGLE_APPLICATION_CREDENTIALS environment variable for the test session.
    """
    with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': 'path/to/your/credentials.json'}):
        yield

@pytest.fixture
def sample_pdf_file():
    """
    Fixture to create a sample PDF file for testing.
    """
    return os.path.join(os.path.dirname(__file__), 'resources', 'sample.pdf')