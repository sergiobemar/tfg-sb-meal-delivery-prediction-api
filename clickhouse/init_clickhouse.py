from src.data.ClickhouseClient import ClickhouseClient

import json
import os
import pandas as pd

if __name__ == "__main__":
	
	# Get Clickhouse credentials and connect
	filename_credentials = '.credentials/clickhouse_credentials.json'
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
	filename_init_config = 'clickhouse/clickhouse_config.json'
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

	# Create schema processed
	database = 'processed'
	client.drop_database(database)
	client.create_database(database)

	# Join train and test tables with center and meal data
	## Train table
	table_name = "train"

	client.drop_table(database=database, table_name=table_name)
	client.execute("""
		CREATE TABLE IF NOT EXISTS """ + database + """.""" + table_name + """ 
		ENGINE = Memory AS
		(
			SELECT
				t.id AS id,
				t.week AS week,
				t.center_id AS center_id,
				t.meal_id AS meal_id,
				t.checkout_price AS checkout_price,
				t.base_price AS base_price,
				t.emailer_for_promotion AS emailer_for_promotion,
				t.homepage_featured AS homepage_featured,
				t.num_orders AS num_orders,
				c.city_code AS city_code,
				c.region_code AS region_code,
				c.center_type AS center_type,
				c.op_area AS op_area,
				m.category AS category,
				m.cuisine AS cuisine
			FROM raw.train t
			LEFT JOIN raw.center c ON c.center_id = t.center_id
			LEFT JOIN raw.meal m ON m.meal_id = t.meal_id
		)
	""")

	## Test table
	table_name = "test"

	client.drop_table(database=database, table_name=table_name)
	client.execute("""
		CREATE TABLE IF NOT EXISTS """ + database + """.""" + table_name + """ 
		ENGINE = Memory AS
		(
			SELECT
				t.id AS id,
				t.week AS week,
				t.center_id AS center_id,
				t.meal_id AS meal_id,
				t.checkout_price AS checkout_price,
				t.base_price AS base_price,
				t.emailer_for_promotion AS emailer_for_promotion,
				t.homepage_featured AS homepage_featured,
				c.city_code AS city_code,
				c.region_code AS region_code,
				c.center_type AS center_type,
				c.op_area AS op_area,
				m.category AS category,
				m.cuisine AS cuisine
			FROM raw.test t
			LEFT JOIN raw.center c ON c.center_id = t.center_id
			LEFT JOIN raw.meal m ON m.meal_id = t.meal_id
		)
	""")
