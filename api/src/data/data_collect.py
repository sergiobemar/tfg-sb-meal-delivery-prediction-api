import numpy as np
import pandas as pd

from api.src.clickhouse.ClickhouseClient import ClickhouseClient

def read_test_data(client: ClickhouseClient):
	# df_test = pd.read_csv('./api/data/processed/test.csv', sep = ';', decimal=',')

	df_test = client.query_dataframe('SELECT * FROM processed.test')
	return df_test

def read_train_data(client: ClickhouseClient):
	#df_train = pd.read_csv('./api/data/processed/train.csv', sep = ';', decimal=',')

	df_train = client.query_dataframe('SELECT * FROM processed.train')
	return df_train
