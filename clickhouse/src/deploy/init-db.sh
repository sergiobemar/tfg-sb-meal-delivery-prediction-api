#!/bin/bash
set -e

#clickhouse client -n <<-EOSQL
#	-- Create raw database
#	CREATE DATABASE IF NOT EXISTS raw;
#	
#	-- Create raw tables
#	CREATE TABLE IF NOT EXISTS raw.center (center_id Int64, city_code Int32, region_code Int32 , center_type String, op_area Float32) ENGINE = Memory;
#	CREATE TABLE IF NOT EXISTS raw.train (id Int64, week Int16, center_id Int64, meal_id Int64, checkout_price Float32, base_price Float32, emailer_for_promotion Int8, homepage_featured Int8, num_orders Int32) ENGINE = Memory;
#	CREATE TABLE IF NOT EXISTS raw.test (id Int64, week Int16, center_id Int64, meal_id Int64, checkout_price Float32, base_price Float32, emailer_for_promotion Int8, homepage_featured Int8) ENGINE = Memory;
#EOSQL

#clickhouse-client --format_csv_delimiter="," --query="INSERT INTO raw.meal FORMAT CSVWithNames" < /var/lib/clickhouse/user_files/meal_info.csv

clickhouse-client --query="CREATE DATABASE IF NOT EXISTS raw;"
clickhouse-client --query="CREATE TABLE IF NOT EXISTS raw.meal (meal_id Int64, category String, cuisine String) ENGINE = Memory;"
