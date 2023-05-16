import tensorflow as tf

colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]

def preprocess(products,landmarks):
    unique_list = list(set(tuple(inner_list) for inner_list in landmarks))
    unique_list_of_lists = [list(inner_tuple) for inner_tuple in unique_list]
    landmarks = unique_list_of_lists

    unique_list = list(set(tuple(inner_list) for inner_list in products))
    unique_list_of_lists = [list(inner_tuple) for inner_tuple in unique_list]
    products = unique_list_of_lists

def create_time_stamp_order(landmarks):
    landmark_dict = {}
    for landmark in landmarks:
         for i in range(len(landmark.timestamp)) :
             landmark_dict[str(landmark.timestamp[i])] = []
    for landmark in landmarks:
         for i in  range(len(landmark.timestamp)) :
             landmark_dict[str(landmark.timestamp[i])].append([landmark.id, landmark.rssi[i], landmark.timestamp[i]])
    for key in landmark_dict.keys():
        labels = {}
        if len(landmark_dict[key])>=8:
            for i in landmark_dict[key]:
                labels[i[0]] = -91
            for i in landmark_dict[key]:
                if i[1]>labels[i[0]]:
                    labels[i[0]] = i[1]
                landmark_dict[key] = [[k, labels[k], key] for k in labels.keys()]
    return landmark_dict

def run_model(products, landmarks):
    inputs= []
    #preprocess(products,landmarks)
    landmark_dict = create_time_stamp_order(landmarks)
    for product in products:
        input = []
        for i in range(len(product.timestamp)):
            input = []
            for j in landmark_dict[str(product.timestamp[i])]:
                input.append(j[1])
            input.append(product.rssi[i])
            inputs.append(input)
    model = tf.keras.models.load_model('model2')
    outputs = model.predict(inputs)
    outputs = outputs.tolist()
    #print(outputs[2])
    output_labels= []
    for output in outputs:
        i= output.index(max(output))
        output_labels.append("L"+str(i))
    
    index = 0
    for product in products:
        for i in range(len(product.timestamp)):
            product.predicted_landmark_id = output_labels[index]
            product.color = colors[int(output_labels[index][-1])]
            index+=1
    return products

