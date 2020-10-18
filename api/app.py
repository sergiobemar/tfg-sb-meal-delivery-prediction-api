import joblib
import json
import numpy as np
import os
import pandas as pd
import sys

from datetime import timedelta
from fastapi import FastAPI

#os.chdir('/home/jupyter/tfg-sb-meal-delivery-prediction/')

from api.src.data.data_collect import read_test_data, read_train_data
from api.src.model.xgboost_model import get_predictions, preprocess_data, train_xgboost_model
from api.src.schema import schema
app = FastAPI(title = 'Predicción de pedidos API') 

# Read datasets
df_test = read_test_data()
df_train = read_train_data()

# Load model
regressor_model = joblib.load('./api/models/xgboost_model.pkl')
# features = joblib.load('./models/xgboost_features.pkl')

@app.get('/predict')
def predict(order : schema.Order):
	
	# Load model
	regressor_model = joblib.load('./api/models/xgboost_model.pkl')
# 	features = joblib.load('./models/xgboost_features.pkl')

	# Get center and meal from the request
	# content = request.json
	
	center_id = order.center_id
	meal_id = order.meal_id

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
	
	return result

@app.get('/test')
def test():
	return {
		'message': 'test successful!!!!!',
		'test' : str(df_train.size)
	}

@app.post('/test_params')
def test_params(order : schema.Order):

	return {
		'message' : 'Params received',
		'center_id' : str(order.center_id),
		'meal_id' : str(order.meal_id)
	}

@app.post('/train')
def train(order : schema.Order):
		
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