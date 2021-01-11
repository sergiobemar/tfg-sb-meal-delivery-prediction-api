from clickhouse_driver import Client
from csv import DictReader

import os
import pandas as pd

class ClickhouseClient(Client):

	def __init__(self, host, port, user, password, database):
		"""
		Creates an instance inherited of clickhouse-driver.Client, then its constructor inits the Clickhouse connection

		Args:
			host (str): the IP of the Clickhouse server
			port (int): the port which is opened in order to connect to Clickhouse server
			user (str): the username which is going to be connected to Clickhouse server
			password (str): user's password in Clickhouse
			database (str): which is the database where is going to be connected
		"""

		# Set script name
		self.script_name = os.path.basename(__file__) + ": "

		# Create connection
		Client.__init__(
			self,
			host = host,
			port = port,
			user = user,
			password = password,
			verify = True,
			database = database,
			compression = True,
			settings = {'use_numpy' : True}
		)

		print(self.script_name + "connection to " + host + " done")

	def create_database(self, database, if_not_exists = True):
		"""
		Creates a named database in the Clickhouse server

		Args:
			database (str): name of the database which is going to be created
			if_not_exists (bool, optional): flag in order to create the database if it doesn't exists, due to prevent an error. Defaults to True.
		"""

		# Check exists flag
		if if_not_exists:
			sentence = 'CREATE DATABASE IF NOT EXISTS ' + database
		else:
			sentence = 'CREATE DATABASE ' + database

		self.execute(sentence)

		print(self.script_name + "database " + database + " created")

	def create_table(self, table_name, database, fields, if_not_exists = True):
		"""
		Creates a table in a specific schema setting the fields that it will contain, in addition, the flag "if_not_exists" allows to avoid the error due to the existence of the table.

		Args:
			table_name (str): name of the table which is going to be created
			database (str): name of the database where is going to be created the table
			fields (list of dicts): list of fields that will build the schema of the table, setting both the name and the type. The schema would be the following:
				[
					{"name" : "field1", "type" : "type1"},
					{"name" : "field2", "type" : "type2"},
					{"name" : "field3", "type" : "type3"}
				]
			if_not_exists (bool, optional): flag in order to create the table if it doesn't exists, due to prevent an error. Defaults to True.
		"""
		
		# Build create sentence
		sentence_first = "CREATE TABLE"

		## Check exists flag
		if if_not_exists:
			sentence_if = " IF NOT EXISTS "
		else:
			sentence_if = " "

		## Get fields and format the sentence
		list_fields = list()
		for s in fields:
			list_fields.append(s['name'] + ' ' + s['type'])

		## Whole sentence
		sentence = sentence_first + sentence_if + database + '.' + table_name + ' (' + ', '.join(list_fields) + ') ENGINE = Memory'

		self.execute(sentence)

		print(self.script_name + "table " + table_name + " created")

	def drop_database(self, database, if_exists = True):
		"""
		Delete a specific database, in addition the flag "if_exists" allows to avoid the error due to existance of the database

		Args:
			database (str): the name of the database that would be deleted
			if_exists (bool, optional): prevents the error due to the existance in advance. Defaults to True.
		"""

		# Build drop sentence
		sentence_first = 'DROP DATABASE'

		# Check exists flag
		if if_exists:
			sentence_if = " IF EXISTS "
		else:
			sentence_if = " "

		sentence = sentence_first + sentence_if + database

		# Execute sentence
		self.execute(sentence)

		print(self.script_name + "database " + database + " created")

	def drop_table(self, table_name, database, if_exists = True):
		"""
		Delete a specific table stored in a database, in addition the flag "if_exists" allows to avoid the error due to existance of the table

		Args:
			table_name (str): the name of the table that is going to be deleted
			database (str): the name of the schema where the table is stored
			if_exists (bool, optional): prevents the error due to the existance in advance. Defaults to True.
		"""

		# Build drop sentence
		sentence_first = 'DROP TABLE'

		# Check exists flag
		if if_exists:
			sentence_if = ' IF EXISTS '
		else:
			sentence_if = ' '
		
		sentence = sentence_first + sentence_if + database + '.' + table_name

		# Execute sentence
		self.execute(sentence)

		print(self.script_name + 'table ' + table_name + ' deleted')

	def insert_csv_file_into_table(self, table_name, file, schema, database = 'default', separator = ','):		
		"""
		Load a table in a Clickhouse server using a CSV file iterating over its rows

		Args:
			table_name (str) : the name of the table
			file (File): file object of the CSV file
			schema (dict) : structure of the file, example:
				{
					"column_name_1" : int,
					"column_name_2" : str,
					"column_name_3" : float,
				}
			database (str) : the name of the database where the table is going to be stored
			separator (str, optional): [description]. Defaults to ",". The separator of the csv file
		
		Returns:
			rows (int): Number of rows inserted into the table
		"""
		# Read csv file
		df = pd.read_csv(file.file, sep=separator)

		# Check schema and cast every columns to the target type
		df = df.astype(schema)

		# Insert into Clickhouse table
		self.insert_dataframe_into_table(table_name, database, df)
		
		return len(df)

	def insert_dataframe_into_table(self, table_name, database, df):
		"""
		In order to avoid the use of the method of clickhouse-driver.Client.insert_dataframe, due to be more verbosed as it's needed to set the INSERT sentence, this function allow the user to insert the dataframe values into a table saved in a specific schema.

		Args:
			table_name (str): name of the table where is going to be saved the values
			database ([type]): name of the database where the table is stored
			df (Pandas.DataFrame): dataframe of values which will be stored into the table
		"""

		sentence = 'INSERT INTO ' + database + '.' + table_name + ' VALUES'
		self.insert_dataframe(sentence, df)

	def iter_csv(self, filename, schema):
		'''
		Iter over csv data checking its structure using the schema

		Args:
			filename (str): the path of the csv file
			schema (dict): the schema of the input csv file

		Returns: every row of the file iteratively
		'''

		with open(filename, 'r') as f:
			reader = DictReader(f)
			for line in reader:
				yield {k: (schema[k](v) if k in schema else v) for k, v in line.items()}
	
	def iter_csv_file(self, file, schema):
		'''
		Iter over csv data checking its structure using the schema

		Args:
			file (File): the file which is going to be read
			schema (dict): the schema of the input csv file

		Returns: every row of the file iteratively
		'''

		reader = DictReader(file)
		for line in reader:
			yield {k: (schema[k](v) if k in schema else v) for k, v in line.items()}

	def load_table_from_csv(self, table_name, file_path, schema, database = 'default'):
		'''
		Load a table in a Clickhouse server using a CSV file iterating over its rows

		Args:
			table_name (str) : the name of the table
			file_path (str) : the path of the CSV file
			schema (dict) : structure of the file, example:
				{
					"column_name_1" : int,
					"column_name_2" : str,
					"column_name_3" : float,
				}
			database (str) : the name of the database where the table is going to be stored
		'''

		self.execute("INSERT INTO " + database + "." + table_name + " VALUES", self.iter_csv(file_path, schema))