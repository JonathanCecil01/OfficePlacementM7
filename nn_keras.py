import tensorflow as tf
import pandas as pd

colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]    #set of colors for each landmark


def run_model(products, landmarks,active_landmarks, color_dict):    #running saved model from the ipnb 
    df = pd.read_csv('classified_data.csv')
    product_label = df['EPC'].to_list()
    inputs = df[['RSSI', 'count', 'locationRSSIL0', 'locationCountL0', 'locationRSSIL1', 'locationCountL1', 'locationRSSIL2', 'locationCountL2', 'locationRSSIL3', 'locationCountL3', 'locationRSSIL4', 'locationCountL4', 'locationRSSIL5', 'locationCountL5', 'locationRSSIL6', 'locationCountL6', 'locationRSSIL7', 'locationCountL7','locationRSSIL0L0', 'locationCountL0L0', 'locationRSSIL0L1', 'locationCountL0L1', 'locationRSSIL0L2', 'locationCountL0L2', 'locationRSSIL0L3', 'locationCountL0L3', 'locationRSSIL1L0', 'locationCountL1L0', 'locationRSSIL1L1', 'locationCountL1L1', 'locationRSSIL1L2', 'locationCountL1L2', 'locationRSSIL1L3', 'locationCountL1L3', 'locationRSSIL2L0', 'locationCountL2L0', 'locationRSSIL2L1', 'locationCountL2L1', 'locationRSSIL2L2', 'locationCountL2L2', 'locationRSSIL2L3', 'locationCountL2L3', 'locationRSSIL3L0', 'locationCountL3L0', 'locationRSSIL3L1', 'locationCountL3L1', 'locationRSSIL3L2', 'locationCountL3L2', 'locationRSSIL3L3', 'locationCountL3L3', 'locationRSSIL4L0', 'locationCountL4L0', 'locationRSSIL4L1', 'locationCountL4L1', 'locationRSSIL4L2', 'locationCountL4L2', 'locationRSSIL4L3', 'locationCountL4L3', 'locationRSSIL5L0', 'locationCountL5L0', 'locationRSSIL5L1', 'locationCountL5L1', 'locationRSSIL5L2', 'locationCountL5L2', 'locationRSSIL5L3', 'locationCountL5L3', 'locationRSSIL6L0', 'locationCountL6L0', 'locationRSSIL6L1', 'locationCountL6L1', 'locationRSSIL6L2', 'locationCountL6L2', 'locationRSSIL6L3', 'locationCountL6L3', 'locationRSSIL7L0', 'locationCountL7L0', 'locationRSSIL7L1', 'locationCountL7L1', 'locationRSSIL7L2', 'locationCountL7L2', 'locationRSSIL7L3', 'locationCountL7L3']]
    model = tf.keras.models.load_model('count_included_nn')           #loading the model 
    outputs = model.predict(inputs)                                 #prediction
    outputs = outputs.tolist()                                      #convertign to list
    output_labels= []
    for output in outputs:
        i= output.index(max(output))
        output_labels.append("L"+str(i))                            #Converting the list of prediction to string
    print(len(product_label), len(output_labels))

    for i in range(len(product_label)):
        for product in products:
            if product.item_no == product_label[i]:
                product.predicted_landmark_ids.append(output_labels[i])
                #product.color = color_dict[product.predicted_landmark_id]
    
    #return products
    # index = 0
    # for product in products:
    #     for i in range(len(product.timestamp)):
    #         product.predicted_landmark_ids.append(output_labels[index]) #setting the predicted label of the product to the list of predicted labels
    #         index+=1
    for product in products:
        product.predicted_landmark_id = max(product.predicted_landmark_ids, key = product.predicted_landmark_ids.count) #finding the most frequent occurance of the predicted location
        product.color = color_dict[product.predicted_landmark_id]       #setting the colour of the product w.r.t. the predicted location
    return products



