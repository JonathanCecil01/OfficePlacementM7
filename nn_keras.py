import tensorflow as tf

colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]    #set of colors for each landmark


def create_time_stamp_order(landmarks, active_landmarks):   #create a dictionary of landmarks arranged according to time
    landmark_dict = {}
    for landmark in landmarks:  #initialize the dictionary
         for i in range(len(landmark.timestamp)) :
             landmark_dict[str(landmark.timestamp[i])] = []
    for landmark in landmarks:  #set for the passive landmark tags
         for i in  range(len(landmark.timestamp)) :
             landmark_dict[str(landmark.timestamp[i])].append([landmark.id, landmark.rssi[i]])
    for landmark in active_landmarks:   #set for the active landmark tags
        for i in range(len(landmark.timestamp)) :
            landmark_dict[str(landmark.timestamp[i])].append([landmark.id, landmark.rssi[i]])

    for key in landmark_dict.keys():
        labels = {}
        if len(landmark_dict[key])>40:  #checking that there is only one reading per location tag for a particular timestamp
            for i in landmark_dict[key]:
                labels[i[0]] = -91
            for i in landmark_dict[key]:
                if i[1]>labels[i[0]]:
                    labels[i[0]] = i[1]
                landmark_dict[key] = [[k, labels[k]] for k in labels.keys()]
    for value in landmark_dict.values():
        value.sort(key = lambda x: x[0])    #soring the order of the landmarks according to the labels, for input layer of NN

    return landmark_dict

def run_model(products, landmarks,active_landmarks, color_dict):    #running saved model from the ipnb 
    inputs= []                                                      #list of inputs initialized 
    landmark_dict = create_time_stamp_order(landmarks, active_landmarks)    #create the time stamp order
    for product in products:                                        #arrange the products accroding to the time stamp order
        input = []
        for i in range(len(product.timestamp)):
            input = []
            for j in landmark_dict[str(product.timestamp[i])]:
                input.append(j[1])                                  #setting each input to the corresponding landmark 
            input.append(product.rssi[i])
            inputs.append(input)
    model = tf.keras.models.load_model('41nn_time_range')           #loading the model (best = 41nn_time_range, otherwise change input node count to 8 and use nn_time_range)
    outputs = model.predict(inputs)                                 #prediction
    outputs = outputs.tolist()                                      #convertign to list
    output_labels= []
    for output in outputs:
        i= output.index(max(output))
        output_labels.append("L"+str(i))                            #Converting the list of prediction to string
    
    index = 0
    for product in products:
        for i in range(len(product.timestamp)):
            product.predicted_landmark_ids.append(output_labels[index]) #setting the predicted label of the product to the list of predicted labels
            index+=1
    for product in products:
        product.predicted_landmark_id = max(product.predicted_landmark_ids, key = product.predicted_landmark_ids.count) #finding the most frequent occurance of the predicted location
        product.color = color_dict[product.predicted_landmark_id]       #setting the colour of the product w.r.t. the predicted location
    return products



