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
#from api.src.model.xgboost_model import get_predictions, preprocess_data, train_xgboost_model

app = FastAPI(title = 'Predicción de pedidos API') 

# Read datasets
df_test = read_test_data()
df_train = read_train_data()

# Load model
regressor_model = joblib.load('./api/models/xgboost_model.pkl')
# features = joblib.load('./models/xgboost_features.pkl')

@app.get('/test')
def get():
	return {
		'message': 'test successful!!!!!',
		'test' : str(df_train.size)
	}

