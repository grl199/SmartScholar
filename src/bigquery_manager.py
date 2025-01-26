'''
Class to manage BigQuery table operations such as creating a table,
'''

import logging
import os
import streamlit as st

import constants
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

logger = logging.getLogger('bigquery_manager')

class BigQueryTableManager:
    """
    A class to manage BigQuery table operations such as creating a table,
    adding rows, and reading the table.
    """
    def __init__(self, config):
        """
        Initializes the BigQueryTableManager with the table ID and BigQuery client.
        """

        project_id = config.get('bigquery').get('project_id',constants.PROJECT_ID)
        dataset_id = config.get('bigquery').get('dataset_id',constants.DATASET_ID)
        table_name = config.get('bigquery').get('table_name',constants.TABLE_NAME)

        self.table_id = f"{project_id}.{dataset_id}.{table_name}"

        logger.info('Initializing BigQuery client...')
        if constants.STORAGE_PROVIDER_CREDENTIALS not in os.environ:
            logger.warning(f'{constants.STORAGE_PROVIDER_CREDENTIALS} not set. BigQuery client not initialized.')
            st.warning(f'{constants.STORAGE_PROVIDER_CREDENTIALS} not set. BigQuery client not initialized.')
            self.client = None
        else:
            try:
                self.client = bigquery.Client()
            except Exception as e:
                logger.exception("Error initializing BigQuery client: %s", e)
                self.client = None

        self.config = config


    def clean_up_schema(self):
        schema = [
        bigquery.SchemaField(
            field["name"], field["type"], mode=field["mode"], description=field.get("description")
        )
        for field in self.config["bigquery"]["schema"]
        ]
        return schema

    def setup_bq_table(self, schema: list = None):
        """
        Creates a BigQuery table with the given schema.

        Args:
            schema (list): A list of bigquery.SchemaField objects defining the table schema.

        Returns:
            BigQueryTableManager: The instance of the BigQueryTableManager.
        """

        # Create the table in BigQuery

        if self.client:
            try:
                # Check if the table already exists
                self.client.get_table(self.table_id)
                logger.info('Table already exists.')
            except NotFound:
                # Define the table

                if not schema:
                    schema = self.clean_up_schema()

                table = bigquery.Table(self.table_id, schema=schema)

                # Create the table in BigQuery
                self.client.create_table(table)
                logger.info('Table created successfully!')


        return self
        
    def add_row(self, row):
        """
        Inserts a row into the BigQuery table.

        Args:
            row (dict): A dictionary representing the row to be inserted.

        Returns:
            BigQueryTableManager: The instance of the BigQueryTableManager.
        """
        # Insert the row into the table
        if self.client:
            self.client.insert_rows_json(self.table_id, [row])  # Wrap row in a list
            st.success("Row inserted successfully!")
        else:
            st.warning("BigQuery client not initialized. Cannot insert row.")
            logger.error("BigQuery client not initialized. Cannot insert row.")
            return self

        return self
    
    def read_table(self):
        """
        Reads the data from the BigQuery table.
        
        TODO: Implement the method to read data from the table.
        """
        return self
