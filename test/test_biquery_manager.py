'''
Test cases for BigQueryManager class
'''

from google.cloud import bigquery


def test_create_table(big_query_manager_instance):

    schema = [
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("age", "INTEGER", mode="REQUIRED"),
    ]
    big_query_manager_instance.setup_bq_table(schema = schema)

def test_add_row(big_query_manager_instance):
    rows = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]
    big_query_manager_instance.add_row(row = rows)

def test_clean_up_schema(big_query_manager_instance):

    big_query_manager_instance.clean_up_schema()

def test_read_table(big_query_manager_instance):

    big_query_manager_instance.read_table()

