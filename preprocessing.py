import pandas as pd
import numpy as np
import csv
from datetime import timedelta


def read_rename():
    rawData = pd.read_csv('rawData.csv')

    #Column Names for Raw Data

    rawDataColumnNames = [
        'locationId',
        'productId',
        'EPC',
        'RSSI',
        'minRSSI',
        'maxRSSI',
        'count',
        'queue',
        'rxPower',
        'session',
        'startTimeStamp',
        'endTimeStamp',
        'isLocation',
        'expectedLocation'
    ]

    rawData = rawData.rename(columns=dict(zip(rawData.columns, rawDataColumnNames)))
    rawData = rawData.drop_duplicates()
    return rawData

#Function to combine rows within +-200ms and same locationId
#  the below function takes one group at first and then one row at a time
def combine_rows(group):
    combined_rows = pd.DataFrame(columns=group.columns)
    for _, row in group.iterrows():
        timestamp_lower = row['endTimeStamp'] - timedelta(milliseconds=200)##change to 200ms
        timestamp_upper = row['endTimeStamp'] + timedelta(milliseconds=200)
        mask = (group['endTimeStamp'] >= timestamp_lower) & (group['endTimeStamp'] <= timestamp_upper)
        count_sum = group.loc[mask, 'count'].sum()
        timestamp_new = group.loc[mask, 'endTimeStamp'].min()  # Since the timestamps are sorted in ascending order thus minimum timestamp represents the base timestamp since the timestamp used to compare the range is sorted
        new_rssi = group.loc[mask, 'RSSI'].max()
        new_row = pd.Series([row['locationId'], row['productId'], row['EPC'], new_rssi, row['minRSSI'], row['maxRSSI'], count_sum, 0, 30, 0, row['startTimeStamp'], timestamp_new, row['isLocation'], row['expectedLocation']], index=group.columns)
        combined_rows = pd.concat([combined_rows, new_row.to_frame().T], ignore_index=True)
    return combined_rows


# Function to classify locations and counts
def classify_locations(row, rawDataL, result_dict, Value, output):
    end_time = row['endTimeStamp']
    range_start = end_time - pd.Timedelta(milliseconds=200)
    range_end = end_time + pd.Timedelta(milliseconds=200)

    # Filter location dataframe within the time range
    filtered_locations = rawDataL[
        (rawDataL['endTimeStamp'] >= range_start) &
        (rawDataL['endTimeStamp'] <= range_end)
    ]

    if filtered_locations.empty:
        return pd.Series(result_dict)

    # Combine location IDs and sum counts if there are multiple matches
    location_ids = filtered_locations['locationId'].unique()
    counts = filtered_locations.groupby('locationId')['count'].sum().reset_index()
    max_rssi = filtered_locations.groupby('locationId')['RSSI'].max().reset_index()
    timestamp = filtered_locations.groupby('locationId')['endTimeStamp'].min().reset_index()
    #outDict = result_dict
    check1 = Value
    #checkDict = grouped_dict
    outDict = {}
    for element in output:
        outDict[element] = 0
        
    for i in range(len(location_ids)):
        #for key in checkDict.keys():
         for key in check1:
            if location_ids[i] == key:    
                outDict['locationId'+location_ids[i]]=location_ids[i]
                outDict['locationRSSI'+location_ids[i]]=max_rssi.loc[max_rssi['locationId'] == location_ids[i], 'RSSI'].values[0]
                outDict['locationCount'+location_ids[i]]=counts.loc[counts['locationId'] == location_ids[i], 'count'].values[0]
                outDict['locationEndTimeStamp'+location_ids[i]]=timestamp.loc[timestamp['locationId'] == location_ids[i], 'endTimeStamp'].values[0]

    return pd.Series(outDict)



def preprocess():
    rawData = read_rename()
    rawDataP = rawData[rawData["isLocation"] == False] #product
    rawDataP.reset_index(drop=True)
    rawDataL = rawData[rawData["isLocation"] == True] #location
    rawDataL.reset_index(drop=True)

    #The rawdatap is first sorted based on EPC first and then endtimestamp.
    #The sorted data is then grouped by EPC
    #Then only 10% data of the maximum RSSI is selected in each group
    #Then the index is reset (removing the grouping)
    #The data is grouped based on EPC, and and the combine row function is applied on each group
    #Using for loop each row is selected in the combine row and based on the conditions the records are combined

    #Sort the dataframe by 'EPC' and 'endTimeStamp' in ascending order
    rawDataP = rawDataP.sort_values(by=['EPC', 'endTimeStamp'], ascending=[True, True])

    #Reset the index
    rawDataP = rawDataP.reset_index(drop=True)

    #Convert 'endTimeStamp' column to datetime objects
    rawDataP['endTimeStamp'] = pd.to_datetime(rawDataP['endTimeStamp'], format='%Y-%m-%d %H:%M:%S.%f')

    #Group by 'productId' and select only the top 10% of readings from each group
    groupedRawDataP = rawDataP.groupby('EPC')
    selectedRowsGroupedRawDataP = groupedRawDataP.apply(lambda x: x.nlargest(int(len(x) * 0.1), 'RSSI'))#10% of the maximum rssi in each group ##change to 0.1

    #Reset the index of selected_rows
    selectedRowsGroupedRawDataP = selectedRowsGroupedRawDataP.reset_index(drop=True)

    #Initialize the combined_rows DataFrame outside the loop
    combinedRowsGroupedRawDataP = pd.DataFrame(columns=selectedRowsGroupedRawDataP.columns)

    #Apply the combine_rows function to each group
    for _, group in selectedRowsGroupedRawDataP.groupby('EPC'):
        combinedRowsGroupedRawDataP = pd.concat([combinedRowsGroupedRawDataP, combine_rows(group)], ignore_index=True)
    #combined_rows = selected_rows.groupby('EPC').apply(combine_rows).reset_index(drop=True)

    #Drop duplicate rows based on timestamp and EPC
    combinedRowsGroupedRawDataP = combinedRowsGroupedRawDataP.drop_duplicates(subset=['endTimeStamp', 'EPC'])

    #Reset the index
    combinedRowsGroupedRawDataP = combinedRowsGroupedRawDataP.reset_index(drop=True)

    #Convert 'endTimeStamp' column back to the original format
    #combined_rows['endTimeStamp'] = combined_rows['endTimeStamp'].dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    #Print the modified DataFrame
    combinedRawDataP= combinedRowsGroupedRawDataP

    Value = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L0L0", "L0L1", "L0L2", "L0L3", "L1L0", "L1L1", "L1L2", "L1L3", "L2L0", "L2L1", "L2L2", "L2L3", "L3L0", "L3L1", "L3L2", "L3L3", "L4L0", "L4L1", "L4L2", "L4L3", "L5L0", "L5L1", "L5L2", "L5L3", "L6L0", "L6L1", "L6L2", "L6L3", "L7L0", "L7L1", "L7L2", "L7L3"]

    #output contains all the 120 columns regarding the location Id's
    output = []

    for value in Value:
        output.append("locationId" + value)
        output.append("locationRSSI" + value)
        output.append("locationCount" + value)
        output.append("locationEndTimeStamp" + value)

    #used later
    result_dict = {}

    for element in output:
        result_dict[element] = 0

    #Consolidated Data DataFrame
    consColumnNames = ['productId', 'EPC', 'RSSI', 'count', 'endTimeStamp', 'expectedLocation']
    consData = pd.DataFrame(columns=consColumnNames)
    
    consData['productId'] = combinedRawDataP['productId']
    consData['EPC'] = combinedRawDataP['EPC']
    consData['RSSI'] = combinedRawDataP['RSSI']
    consData['count'] = combinedRawDataP['count']
    consData['endTimeStamp'] = combinedRawDataP['endTimeStamp']
    consData['expectedLocation'] = combinedRawDataP['expectedLocation']
    

    # Convert endTimeStamp columns to datetime
    #consData['endTimeStamp'] = pd.to_datetime(consData['endTimeStamp'])
    #rawDataL['endTimeStamp'] = pd.to_datetime(rawDataL['endTimeStamp'])
    #sorted_data = rawDataL.sort_values('endTimeStamp')
    consData.loc[:, 'endTimeStamp'] = pd.to_datetime(consData['endTimeStamp'])
    rawDataL.loc[:, 'endTimeStamp'] = pd.to_datetime(rawDataL['endTimeStamp'])
    sorted_data = rawDataL.sort_values('endTimeStamp')

    classified_df = consData.merge(consData.apply(lambda row: classify_locations(row, rawDataL, {}, Value, output), axis=1), left_index=True, right_index=True)

    #classified_df = consData.merge(consData.apply(classify_locations(rawDataL, {}, Value, output), axis=1), left_index=True, right_index=True)

    #reorder the columns

    reordercColumns = classified_df.columns.tolist()

    # Move the 'RSSI' column to the last position
    reordercColumns.remove('expectedLocation')
    reordercColumns.append('expectedLocation')

    # Reorder the DataFrame columns
    classified_df = classified_df[reordercColumns]
    print(classified_df)
    classified_df.to_csv('classified_data.csv', index=False)
    return



preprocess()



