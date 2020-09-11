import numpy as np
import os
import pandas as pd
import xgboost as xgb
from sklearn import metrics

def get_predictions(model, df, date_index):
	preds = model.predict(df)
	preds = np.exp(preds)
	
	preds = pd.DataFrame(preds)
	preds = preds.rename(columns={0 : 'num_orders'})
	preds.index = date_index
	
	return preds

def preprocess_data(df, center_id, meal_id, start_date = '2017-01-01'):

	# Select the center and meal
	condition1 = df['center_id'] == int(center_id)
	condition2 = df['meal_id'] == int(meal_id)

	df_processed = df[condition1 & condition2]

	print('DF_PROCESSED: ' + str(len(df_processed)))
	
	# Added date variables
	last_weeks = len(df_processed)
	df_processed.date = pd.date_range(start_date, periods=last_weeks, freq='W')

	df_processed['day'] = df_processed.date.dt.day
	df_processed['month'] = df_processed.date.dt.month
	df_processed['year'] = df_processed.date.dt.year
	df_processed['quarter'] = df_processed.date.dt.quarter

	# Drop non relevant columns
	df_processed = df_processed.drop(columns=['id', 'center_id', 'meal_id', 'center_type', 'category', 'cuisine'])

	# Set date variable as index
	df_processed = df_processed.set_index('date')

	return df_processed

def train_xgboost_model(df_train_processed):

	# Feature enginering and split dataframe
	X = df_train_processed.drop(columns='num_orders')
	Y = np.log1p(df_train_processed['num_orders'])

	split_size = len(df_train_processed) - 15
	X_train = X.iloc[:split_size,:]
	X_test = X.iloc[split_size:,:]
	Y_train =  Y.iloc[:split_size]
	Y_test = Y.iloc[split_size:]

	# Train the model using evaluation set in order to avoid overfitting
	model = xgb.XGBRegressor(
		learning_rate = 0.01,
		eval_metric ='rmse',
		n_estimators = 50000,
		max_depth = 5,
		subsample = 0.8,
		colsample_bytree = 1,
		gamma = 0.5  
	)

	model.fit(
		X_train,
		Y_train,
		eval_metric='rmse',
		eval_set=[(X_test, Y_test)],
		early_stopping_rounds=500,
		verbose=0
	)

	# Get the best iteration and asing to de number of estimators param into the model hyperparameters
	best = model.get_booster().best_iteration

	xgb_model = xgb.XGBRegressor(
		learning_rate = 0.01,
		n_estimators = best,
		max_depth = 5,
		subsample = 0.8,
		colsample_bytree = 1,
		gamma = 0.5
	)

	# Training again
	xgb_model.fit(X_train, Y_train)

	# Get predictions 
	xgb_preds = xgb_model.predict(X_test)

	# Cast target variable aplying exponential function and create a dataframe with them
	xgb_preds = np.exp(xgb_preds)

	xgb_preds = pd.DataFrame(xgb_preds)
	xgb_preds.index = Y_test.index

	# Get accuracy
	Y_train = np.exp(Y_train)
	Y_test = np.exp(Y_test)

	# Get evaluation metric
	mse = metrics.mean_squared_error(Y_test, xgb_preds)
	rmse = np.sqrt(mse)
	print('RMSE: ' + str(rmse))

	return xgb_model, rmse