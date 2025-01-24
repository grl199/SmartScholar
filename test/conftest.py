'''
conftest.py
'''

import os
import pytest

from src.bigquery_manager import BigQueryTableManager
from src.utilities import read_config,set_logger
from src import constants

CONFIG = read_config('test/resources/test_config.yaml')

os.environ['HUGGINGFACEHUB_API_TOKEN'] = \
    os.getenv('HUGGINGFACEHUB_API_TOKEN',constants.DEFAULT_API_KEY)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
    os.getenv('GOOGLE_APPLICATION_CREDENTIALS',constants.DEFAULT_API_KEY)

@pytest.fixture(scope='session', autouse=True)
def config():
    """
    Fixture to get the configuration file for the test session.
    """
    return CONFIG

@pytest.fixture(scope='session', autouse=True)
def logger():
    """
    Fixture to set up the logger for the test session.
    """
    logger_object = set_logger(CONFIG)
    return logger_object


@pytest.fixture(scope='session', autouse=True)
def big_query_manager_instance():
    """
    Fixture to set up the BigQueryTableManager for the test session.
    """
  
    return BigQueryTableManager(CONFIG)

@pytest.fixture
def sample_pdf_file():
    """
    Fixture to create a sample PDF file for testing.
    """
    return os.path.join(os.path.dirname(__file__), 'resources', 'sample.pdf')