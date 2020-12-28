import numpy as np
import pandas as pd

def read_test_data():
	df_test = pd.read_csv('./api/data/processed/test.csv', sep = ';', decimal=',')

	return df_test

def read_train_data(client):
	#df_train = pd.read_csv('./api/data/processed/train.csv', sep = ';', decimal=',')

	df_train = client.query_dataframe('SELECT * FROM processed.train')
	return df_train
