from src.data.ClickhouseClient import ClickhouseClient

import json
import os
import pandas as pd
import sys

if __name__ == "__main__":
	
	# Get Clickhouse credentials and connect
	filename_credentials = 'clickhouse_credentials.json'
	with open(filename_credentials, 'r') as f:
		credentials = json.load(f)

	client = ClickhouseClient(
		host = credentials['host'],
		port = credentials['port'],
		user = credentials['user'],
		password = credentials['password'],
		database = credentials['database']
	)

	# Drop raw schema if not exists, and then it's created again
	database = 'raw'
	client.drop_database(database)
	client.create_database(database)

	# Read initialize config file
	filename_init_config = 'initialize_config.json'
	with open(filename_init_config, 'r') as f:
		config = json.load(f)

	# Read and create the following tables in raw
	for t in config['files']:

		# Create the table
		## First, get the schema and create a table using it in Clickhouse database
		client.create_table(t['table_name'], database, t['schema'])
	
		# Read csv and insert data into its table
		df = pd.read_csv(t['path'])

		client.insert_dataframe_into_table(t['table_name'], database, df)
