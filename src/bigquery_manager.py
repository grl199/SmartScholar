from google.cloud import bigquery
import constants
import logging
import os
import Exception

from google.cloud.exceptions import NotFound

logger = logging.getLogger('bigquery_manager')

class BigQueryTableManager:
    """
    A class to manage BigQuery table operations such as creating a table,
    adding rows, and reading the table.
    """
    def __init__(self):
        """
        Initializes the BigQueryTableManager with the table ID and BigQuery client.
        """
        self.table_id = f"{constants.PROJECT_ID}.{constants.DATASET_ID}.{constants.TABLE_NAME}"

        logger.info('Initializing BigQuery client...')

        if os.environ['GOOGLE_APPLICATION_CREDENTIALS']=='None':
            logger.warning('GOOGLE_APPLICATION_CREDENTIALS not set. BigQuery client not initialized.')
            self.client = None
        else:
            try:
                self.client = bigquery.Client()
            except Exception as e:
                logger.exception(f"Error initializing BigQuery client: {e}")
                self.client = None

    def setup_bq_table(self, schema):
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
        else:
            logger.error("BigQuery client not initialized. Cannot insert row.")
            return self

        return self
    
    def read_table(self):
        """
        Reads the data from the BigQuery table.
        
        TODO: Implement the method to read data from the table.
        """
        return self
