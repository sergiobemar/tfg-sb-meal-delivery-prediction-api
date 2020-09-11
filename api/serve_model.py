import joblib
import json
import numpy as np
import os
import pandas as pd
import sys

from datetime import timedelta  
from flask import Flask
from flask import jsonify
from flask import request
# from flask_restful import Api, Resource

#os.chdir('/home/jupyter/tfg-sb-meal-delivery-prediction/')

from src.data.data_collect import read_test_data, read_train_data
from src.model.xgboost_model import get_predictions, preprocess_data, train_xgboost_model

# Read datasets
df_test = read_test_data()
df_train = read_train_data()

# Load model
regressor_model = joblib.load('./models/xgboost_model.pkl')
# features = joblib.load('./models/xgboost_features.pkl')

app = Flask(__name__)
# api = Api(app)

# class Test(Resource):
# 	def get(self):
# 		return {'response': 'test successful!!!!!'}

# class Predict(Resource):
# 	def post(self):
# 		json_data_dict = request.get_json(force=True)
# 		X = json_data_dict['features']
# 		predictions = model.predict(X)
# 		return {'predictions':predictions}

@app.route('/test', methods=['GET'])
def get():
	return {'response': 'test successful!!!!!'}


@app.route('/predict', methods=['POST'])
def predict():
	
	# Load model
	regressor_model = joblib.load('./models/xgboost_model.pkl')
	features = joblib.load('./models/xgboost_features.pkl')

	# Get content from POST request
	content = request.json

	# Read dataframe
	df = pd.DataFrame.from_records(content)
	
	# Set column date as index in order to use it in predictions result
	df = df.set_index('date')
	
	# Select significative columns
	df = df[features]

	# Cast to numeric
	df = df.apply(pd.to_numeric)
	
	# Print num rows
	print('NUM ROWS: ' + str(len(df.index)))
	print(df.columns)
	
	pred = regressor_model.predict(df)
	
	# Use exponential to convert the result
	pred_results = np.exp(pred)
	
	# Create a dataframe with predictions
	df_result = pd.DataFrame({"num_orders" : pred_results})
	
	# Assign index from source dataframe and, so that we're able to have another column with the date, index is reseted
	df_result.index = df.index
	df_result.reset_index(inplace=True)
	
	# Generate a JSON with results
	result = df_result.to_json(orient='records')
	
# 	return pred[0]
# 	result = {
# 		"features" : features,
# 		"columns" : list(df.columns),
# 		"pred" : list(pred[0])
# 	}
# 	print(pred)
# 	result = {df.index[i] : str(pred_results[i]) for i in range(0, len(pred_results))}
	
	return result

@app.route('/predict2', methods=['POST'])
def predict2():
	
	# Load model
	regressor_model = joblib.load('./models/xgboost_model.pkl')
# 	features = joblib.load('./models/xgboost_features.pkl')

	# Get center and meal from the request
	content = request.json
	
	center_id = content['center_id']
	meal_id = content['meal_id']

	print("CENTER: " + str(center_id))
	print("MEAL: " + str(meal_id))
	
# 	cond = np.where((df_train['center_id'] == center_id) & (df_train['meal_id'] == meal_id))
	
# 	print("DF_TRAIN: " + str(len(df_train.iloc[cond])))
	
	# Preprocess test dataframe
	df_train_preprocessed = preprocess_data(df_train, center_id, meal_id) 

	next_day = df_train_preprocessed.index.max().date() + timedelta(days=1)

	df_test_preprocessed = preprocess_data(df_test, center_id, meal_id, next_day)
	
	# Print num rows
	print('NUM ROWS: ' + str(len(df_test_preprocessed.index)))	
	print('NEXT_DATE: ' + str(next_day))
	print(df_test_preprocessed.columns)
	
# 	pred = regressor_model.predict(df_test_preprocessed[features])
	
# 	# Use exponential to convert the result
# 	pred_results = np.exp(pred)
	
# 	# Create a dataframe with predictions
# 	df_result = pd.DataFrame({"num_orders" : pred_results})
	
# 	# Assign index from source dataframe and, so that we're able to have another column with the date, index is reseted
# 	df_result.index = df_test_preprocessed.index
	print(df_test_preprocessed)
	df_result = get_predictions(regressor_model, df_test_preprocessed, df_test_preprocessed.index)
	df_result.reset_index(inplace=True)
	df_result['date'] = df_result.date
	
# 	for i in df_result.date:
# 		print("FECHA: " + str(i))

	# Generate a JSON with results
	result = df_result.to_json(orient='records', date_format = 'iso')
	
	print(result)
	
	return result

@app.route('/save', methods=['GET'])
def save_model():
	
	joblib.dump(regressor_model, './models/xgboost_model.pkl')
# 	joblib.dump(features, './models/xgboost_features.pkl')
	
	return {'response': 'Model saved done!'}

@app.route('/train', methods=['POST'])
def train():
	
	# Get center and meal from the request
	content = request.json
	
	center_id = int(content['center_id'])
	meal_id = int(content['meal_id'])
	
	print("CENTER: " + str(center_id))
	print("MEAL: " + str(meal_id))
	
	# Preprocess the dataframe
	df_preprocessed = preprocess_data(df_train, center_id, meal_id)
	
	select_cols = ['week', 'checkout_price', 'base_price', 'emailer_for_promotion', 'homepage_featured', 'num_orders', 'city_code', 'region_code', 'op_area', 'month', 'quarter']
	
	print("SIZE: " + str(len(df_train)))
	
	# Train the model
# 	regressor_model, rmse = train_xgboost_model(df_preprocessed[select_cols])
	regressor_model, rmse = train_xgboost_model(df_preprocessed)

# 	features = list(df_preprocessed[select_cols].drop(columns='num_orders').columns)
	
	# Save the model and features
	joblib.dump(regressor_model, './models/xgboost_model.pkl')
# 	joblib.dump(features, './models/xgboost_features.pkl')
	
	# Return dict results
	result = {
# 		'features' : features,
		'rmse' : rmse
# 		'rmse' : str(len(df_preprocessed))
	}
# 	result = {
# 		'data' : content['center_id']
# 	}
	return jsonify(result)

if __name__ == '__main__':
	
	# Run server
	app.run(debug=True, host='0.0.0.0', port=5000)
