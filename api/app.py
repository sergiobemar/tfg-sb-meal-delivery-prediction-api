import joblib
import json
import numpy as np
import os
import pandas as pd
import sys

from datetime import timedelta
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List

from api.src.data.data_collect import read_test_data, read_train_data
from api.src.model.xgboost_model import get_predictions, preprocess_data, train_xgboost_model
from api.src.schema import schema

from api.src.clickhouse.ClickhouseClient import ClickhouseClient

# FastAPI specification
tags_metadata = [
	{
		"name" : "prediction",
		"description" : "Operations in order to make the prediction."
	},
	{
		"name" : "data",
		"description" : "Show and get the data from database. For this procedure it's used the module `clickhouse-driver` plus a class that inherits from it.",
		"externalDocs" : {
			"description" : "For more information see its website",
			"url" : "https://clickhouse-driver.readthedocs.io/en/latest/"
		}
	},
	{
		"name" : "upload",
		"description" : "Operations in order to upload data and insert it to the specific tables into the Clickhouse database."
	},
	{
		"name" : "test",
		"description" : "Some methods in order to test API functionality."
	}
]

app = FastAPI(
	title = "Meal Orders Prediction API",
	description = "This API provides the developer the information and also the prediction calculation about the delivery meal center.",
	version = "2.0",
	openapi_tags = tags_metadata
) 

# Read Clickhouse credentials and connect to the database
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

# Read datasets
df_test = read_test_data(client)
df_train = read_train_data(client)

# Load model
regressor_model = joblib.load('./api/models/xgboost_model.pkl')

# Data methods
@app.get('/data/center', response_model = List[schema.Center], tags=["data"])
async def get_center(limit: int = 10):
	"""
	Get original center data from Clickhouse

	Args:
		
		limit (int, optional): set the limit of rows that user need. If this value is 0, it's returned whole dataframe. Defaults to 10.

	Returns:
		
		List Center data: rows from center data
	"""

	# Receive the data from Clickhouse
	df = client.query_dataframe('SELECT * FROM raw.center')

	# Transform the dataframe into JSON format in order to be able to send it through the API method
	if limit == 0:
		result = df.to_json(orient='records')
	else:
		result = df.head(limit).to_json(orient='records')
	
	return JSONResponse(content=result)

@app.get('/data/meal', response_model = List[schema.Meal], tags=["data"])
async def get_meal(limit: int = 10):
	"""
	Get original meal data from Clickhouse

	Args:
		
		limit (int, optional): set the limit of rows that user need. If this value is 0, it's returned whole dataframe. Defaults to 10.

	Returns:
		
		List Meal data: rows from meal data
	"""

	# Receive the data from Clickhouse
	df = client.query_dataframe('SELECT * FROM raw.meal')

	# Transform the dataframe into JSON format in order to be able to send it through the API method
	if limit == 0:
		result = df.to_json(orient='records')
	else:
		result = df.head(limit).to_json(orient='records')
	
	return JSONResponse(content=result)

@app.get('/data/test', response_model = List[schema.DataModel], tags=["data"])
async def get_test_data():
	"""
	Get a sample from test dataframe

	Returns:
		
		List Test data: sample of test data
	"""

	# Transform the dataframe into JSON format in order to be able to send it through the API method
	result = df_test.head().to_json(orient='records')
	
	return JSONResponse(content=result)

@app.get('/data/train', response_model = List[schema.DataModel], tags=["data"])
async def get_train_data():
	"""
	Get a sample from train dataframe

	Returns:
		
		List Train data: sample of train data
	"""

	# Transform the dataframe into JSON format in order to be able to send it through the API method
	result = df_train.head().to_json(orient='records')
	
	return JSONResponse(content=result)

@app.get('/data/refresh', tags=["data"])
async def refresh_prediction_data():
	"""
	Refresh the data from Clickhouse server updating train and test dataframes.

	Raises:
		
		HTTPException: 404 error if API couldn't refresh the data from Clickhouse

	Returns:
		
		Message (str): shows if the process was ok
	"""

	df_test_new = read_test_data(client)
	df_train_new = read_train_data(client)

	if (df_test_new.empty) | (df_train_new.empty):
		raise HTTPException(status_code = 404, detail='Error in refresh process')
	else:
		df_test = df_test_new
		df_train = df_train_new.copy()

	return {"message" : "Dataframe were updating"}

# Prediction methods
@app.get('/predict', response_model = List[schema.Prediction], tags=["prediction"])
async def predict(center_id : int, meal_id : int):
	"""
	When a model has been trained, this method recovers serialized model in order to make a prediction with it.
	In addition, so that the function managed to return the other fields of prediction data, besides the number of predicted orders, it's needed center and meal identifiers.

	Args:
		
		center_id (int): identifier of the center to be predicted
		
		meal_id (int): identifier of the meal to be predicted

	Rerturns:
		
		List Prediction data: number of orders by date in the following 10 weeks
	"""

	# Load model
	regressor_model = joblib.load('./api/models/xgboost_model.pkl')
 	# features = joblib.load('./models/xgboost_features.pkl')

	# Get center and meal from the request
	# content = request.json
	
	#center_id = order.center_id
	#meal_id = order.meal_id

	print("CENTER: " + str(center_id))
	print("MEAL: " + str(meal_id))
	
	# Preprocess test dataframe
	df_train_preprocessed = preprocess_data(df_train, center_id, meal_id) 

	next_day = df_train_preprocessed.index.max().date() + timedelta(days=1)

	df_test_preprocessed = preprocess_data(df_test, center_id, meal_id, next_day)
	
	# Print num rows and dataframe
	print('NUM ROWS: ' + str(len(df_test_preprocessed.index)))	
	print(df_test_preprocessed)
	
 	# Assign index from source dataframe and, so that we're able to have another column with the date, index is reseted
	df_result = get_predictions(regressor_model, df_test_preprocessed, df_test_preprocessed.index)
	df_result.reset_index(inplace=True)
	df_result['date'] = df_result.date

	# Generate a JSON with results
	result = df_result.to_json(orient='records', date_format = 'iso')
	
	print(result)
	
	return JSONResponse(content=result)

@app.post('/train', tags=["prediction"])
async def train(order : schema.OrderTrain):
	"""
	Train a XGBoost model using the center and meal id.
	When model is trained, it will be saved as Pickel in order to recover it when it was necessary to make a prediction.

	Args:
		
		order (schema.OrderTrain): the center and meal identifier in order to select the historic using them as filter
	
	Rerturns:
		
		rmse (float): the error given by the trained model
	"""
	center_id = order.center_id
	meal_id = order.meal_id
	
	print("CENTER: " + str(center_id))
	print("MEAL: " + str(meal_id))
	
	# Preprocess the dataframe
	df_preprocessed = preprocess_data(df_train, center_id, meal_id)
	
	select_cols = ['week', 'checkout_price', 'base_price', 'emailer_for_promotion', 'homepage_featured', 'num_orders', 'city_code', 'region_code', 'op_area', 'month', 'quarter']
	
	print("SIZE: " + str(len(df_train)))
	
	# Train the model
	regressor_model, rmse = train_xgboost_model(df_preprocessed)

	# Save the model and features
	joblib.dump(regressor_model, './api/models/xgboost_model.pkl')
 	# joblib.dump(features, './models/xgboost_features.pkl')
	
	# Return dict results
	result = {
 		# 'features' : features,
		'rmse' : rmse
	}

	return result

# Test methods
@app.get('/test', tags=["test"])
async def test():
	"""
	Checks if the API is running correctly

	Returns:
		
		message (str): shows a message
	"""
	return {
		'message': 'test successful!!!!!'
	}

@app.get('/test_clickhouse', tags=["test"])
async def test_clickhouse():
	"""
	Test if the connection with Clickhouse is made. If not, this method raises an error
	
	Raises:
		
		HTTPException: 404 error if the connection wan't made

	Returns:
		
		df (dict): sample of rows got from a Clickhouse table
	"""

	df = client.query_dataframe('SELECT * FROM raw.meal LIMIT 10')

	if (df.empty):
		raise HTTPException(status_code = 404, detail='There was an error when it tried to connect to Clickhouse')
	
	return df.to_json(orient='records')

@app.post('/test_params', tags=["test"])
async def test_params(order : schema.OrderTrain):
	"""
	Check if params are being received correctly

	Args:
		
		order (schema.OrderTrain): the center and meal identifier in order to select the historic using them as filter

	Returns:
		
		message (str): shows a simple test string
		
		center_id (str): center identifier given by the input parameter order
		
		meal_id (str): meal identifier given by the input parameter order
	"""

	return {
		'message' : 'Params received',
		'center_id' : str(order.center_id),
		'meal_id' : str(order.meal_id)
	}

@app.post('/test_upload_file', tags=["test"])
async def test_upload_file(file: UploadFile = File(...)):
	"""
	Check the functionality when it's needed to upload a csv file

	Args:
		file (UploadFile, optional): The file that it's going to be uploaded. Defaults to File().
	"""

	dataframe = pd.read_csv(file.file)

	return {
		"filename" : file.filename,
		"rows" : str(len(dataframe))
	}

# Upload data
@app.post('/data/upload', tags=["upload"])
async def upload_data_from_csv(table_name: str, database: str, schema_file : UploadFile = File(...), input_file: UploadFile = File(...), separator: str = ","):
	"""
	Uploads a specific csv file to the table which user wants, setting both the schema of the file and the database

	Args:
		
		table_name (str): the name of the table where is going to be saved the data
		
		database (str): the name of the database where the table is located in
		
		schema (UploadFile, optional): json file with the schema of the input file. The structure of the json file must be the following:

			{
		
				"column_name_1" : "int",
		
				"column_name_2" : "str",
		
				"column_name_3" : "float",
		
			} 
		
		input_file (UploadFile, optional): The csv file that it's wanted to be inserted into the table. Defaults to File(...). 
		
		separator (str, optional): The separator of the csv file. Defaults to ",".

	Raises:
		HTTPException: raised exception when method fails in insert procedure

	Returns:
		filename (str): The name of the uploaded csv
		rows (str): Number of rows inserted into the table
	"""

	# Read the json file
	data_json = json.load(schema_file.file)

	# Cast type strings to object type from json file
	schema = dict()

	for i, j in data_json.items():

		# Column name
		column_name = i
		
		# Type
		if j == 'int':
			column_type = int
		elif j == 'float':
			column_type = float
		else:
			column_type = str
		
		# Added to schema dict
		schema[column_name] = column_type
	
	# Try to insert the csv file into the table
	try:
		rows = client.insert_csv_file_into_table(table_name=table_name, file=input_file, schema=schema, database=database, separator=separator)
	except:
		raise HTTPException(status_code = 404, detail='There was an error when it tried to insert the csv in the file')

	return {
		"filename" : input_file.filename,
		"rows" : str(rows)
	}

@app.post('/data/upload/center', tags=["upload"])
async def upload_data_center(file: UploadFile = File(...), separator: str = ","):
	"""
	Allows the user to upload a csv file of center data to its corresponding table in raw schema.

	The file must be structured like this, being the separator that the user wants:
		
		center_id,city_code,region_code,center_type,op_area

		11,679,56,TYPE_A,3.7

	Args:
		
		file (UploadFile, optional): The csv file with the data of the centers in order to insert into the table. Defaults to File(...). 
		
		separator (str, optional): The separator of the csv file. Defaults to ",".

	Raises:
		
		HTTPException: raised exception when method fails in insert procedure

	Returns:
		
		filename (str): The name of the uploaded csv
		
		rows (str): Number of rows inserted into the table
	"""

	# Defining the schema
	schema = {
		'center_id' : int,
		'city_code' : int,
		'region_code' : int,
		'center_type' : str,
		'op_area' : float
	}

	# Try to insert the csv file into the table
	try:
		rows = client.insert_csv_file_into_table(table_name="center", file=file, schema=schema, database="raw", separator=separator)
	except:
		raise HTTPException(status_code = 404, detail='There was an error when it tried to insert the csv in the file')

	return {
		"filename" : file.filename,
		"rows" : str(rows)
	}

@app.post('/data/upload/meal', tags=["upload"])
async def upload_data_meal(file: UploadFile = File(...), separator: str = ","):
	"""
	Allows the user to upload a csv file of meal data to its corresponding table in raw schema.

	The file must be structured like this, being the separator that the user wants:
		
		meal_id,category,cuisine
		
		1885,Beverages,Thai

	Args:
		
		file (UploadFile, optional): The csv file with the data of the meals in order to insert into the table. Defaults to File(...).
		
		separator (str, optional): The separator of the csv file. Defaults to ",".

	Raises:
		
		HTTPException: raised exception when method fails in insert procedure

	Returns:
		
		filename (str): The name of the uploaded csv
		
		rows (str): Number of rows inserted into the table
	"""

	# Defining the schema
	schema = {
		'meal_id' : int,
		'category' : str,
		'cuisine' : str
	}

	# Try to insert the csv file into the table
	try:
		rows = client.insert_csv_file_into_table(table_name="meal", file=file, schema=schema, database="raw", separator=separator)
	except:
		raise HTTPException(status_code = 404, detail='There was an error when it tried to insert the csv in the file')

	return {
		"filename" : file.filename,
		"rows" : str(rows)
	}

@app.post('/data/upload/predict', tags=["upload"])
async def upload_data_predict(file: UploadFile = File(...), separator: str = ","):
	"""
	Allows the user to upload a csv file of test data to its corresponding table in raw schema.

	The file must be structured like this, being the separator that the user wants:
		
		id,week,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured

		1,1,55,1885,136.83,152.29,0,0

	Args:
		
		file (UploadFile, optional): The csv file with the data of the features of sales in order to insert into the table. Defaults to File(...).
		
		separator (str, optional): The separator of the csv file. Defaults to ",".

	Raises:
		
		HTTPException: raised exception when method fails in insert procedure

	Returns:
		
		filename (str): The name of the uploaded csv
		
		rows (str): Number of rows inserted into the table
	"""

	# Defining the schema
	schema = {
		'id' : int,
		'week' : int,
		'center_id' : int,
		'meal_id' : int,
		'checkout_price' : float,
		'base_price' : float,
		'emailer_for_promotion' : int,
		'homepage_featured' : int
	}

	# Try to insert the csv file into the table
	try:
		rows = client.insert_csv_file_into_table(table_name="test", file=file, schema=schema, database="raw", separator=separator)
	except:
		raise HTTPException(status_code = 404, detail='There was an error when it tried to insert the csv in the file')

	return {
		"filename" : file.filename,
		"rows" : str(rows)
	}

@app.post('/data/upload/train', tags=["upload"])
async def upload_data_train(file: UploadFile = File(...), separator: str = ","):
	"""
	Allows the user to upload a csv file of train data to its corresponding table in raw schema.

	The file must be structured like this, being the separator that the user wants:
		
		id,week,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,num_orders

		1,1,55,1885,136.83,152.29,0,0,177

	Args:
		
		file (UploadFile, optional): The csv file with the data of the historical sales in order to insert into the table. Defaults to File(...).
		
		separator (str, optional): The separator of the csv file. Defaults to ",". 

	Raises:
		
		HTTPException: raised exception when method fails in insert procedure

	Returns:
		
		filename (str): The name of the uploaded csv
		
		rows (str): Number of rows inserted into the table
	"""

	# Defining the schema
	schema = {
		'id' : int,
		'week' : int,
		'center_id' : int,
		'meal_id' : int,
		'checkout_price' : float,
		'base_price' : float,
		'emailer_for_promotion' : int,
		'homepage_featured' : int,
		'num_orders' : int
	}

	# Try to insert the csv file into the table
	try:
		rows = client.insert_csv_file_into_table(table_name="train", file=file, schema=schema, database="raw", separator=separator)
	except:
		raise HTTPException(status_code = 404, detail='There was an error when it tried to insert the csv in the file')

	return {
		"filename" : file.filename,
		"rows" : str(rows)
	}
