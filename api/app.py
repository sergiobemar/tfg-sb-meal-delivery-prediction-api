import joblib
import json
import numpy as np
import os
import pandas as pd
import sys

from datetime import timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List

#os.chdir('/home/jupyter/tfg-sb-meal-delivery-prediction/')

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
		"name" : "test",
		"description" : "Some methods in order to test API functionality."
	}
]

app = FastAPI(
	title = "Predicción de pedidos API",
	description = "Una API para proveer la información así como los cálculos de predicción sobre los pedidos de un centro de reparto de comidas a domicilio.",
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
# 	features = joblib.load('./models/xgboost_features.pkl')

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
	
# 	# Assign index from source dataframe and, so that we're able to have another column with the date, index is reseted
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
# 	joblib.dump(features, './models/xgboost_features.pkl')
	
	# Return dict results
	result = {
# 		'features' : features,
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
		raise HTTPException(status_code = 404, detail='Error, there was an error when it tryed to connect to Clickhouse')
	
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
