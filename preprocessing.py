import csv
import numpy as np 
import pandas as pd 

import pandas as pd

# Read the raw data into a DataFrame
df = pd.read_csv('raw_data.csv')

# Filter the data for products where isLocation is false and productid > 0
filtered_df = df[(df['ProductId'] != 0)]

# Convert timestamp columns to datetime type
filtered_df['start_timestamp'] = pd.to_datetime(filtered_df['start_timestamp'])
filtered_df['end_timestamp'] = pd.to_datetime(filtered_df['end_timestamp'])

# Set the timestamp as the index
filtered_df.set_index('starttimestamp', inplace=True)

# Define the timestamp window duration (500ms in this case)
window_duration = pd.Timedelta(milliseconds=500)

# Group by productid and EPC, and resample within the timestamp window
processed_df = filtered_df.groupby(['productid', 'EPC']).resample(window_duration).agg({
    'count': 'sum',
    'locationld': 'first',
    'rssi': 'first'
})

# Reset the index and drop unnecessary columns
processed_df.reset_index(inplace=True)
processed_df.drop(['starttimestamp', 'endtimestamp', 'isLocation'], axis=1, inplace=True)

# Rename the columns to match the desired format
processed_df.rename(columns={
    'locationld': 'locationID',
    'rssi': 'locationssi'
}, inplace=True)

# Pivot the data to get the desired format
processed_df = processed_df.pivot_table(index=['productid', 'EPC', 'count'], columns='level_2', values=['locationID', 'locationssi'])

# Flatten the column multi-index
processed_df.columns = [f'{col[0]}{col[1]}' for col in processed_df.columns]

# Reset the index
processed_df.reset_index(inplace=True)

# Print the processed data
print(processed_df)
