from office import *
from tags import *
import matplotlib.pyplot as plt
import csv
from nn_keras import *

colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]

def predictions():
    products = []
    with open('Predictions.csv', 'r') as file1:
        reader = csv.reader(file1)
        for row in reader:
            products.append(row) 
    for product in products:
        product[1] = float(product[1])
        
    return products

def K_Means_Clustering(landmarks, products):
    for product in products:
        product.set_max_rssi()
    for landmark in landmarks:
        landmark.set_max_rssi()
    centres  = [[landmark.max_time, landmark.max_rssi] for landmark in landmarks]
    for product in products:
        distances = [math.dist([product.max_time, product.max_rssi], i) for i in centres]
        min_distance = min(distances)
        index_min = distances.index(min_distance)
        product.color = landmarks[index_min].color
        product.predicted_landamrk_id = landmarks[index_min].id
    plot_rssi(products, landmarks)    



def write_data(passive_landmarks, landmarks, products):
    active_landmark_list = []
    for landmark in landmarks:
        for i in range(0, len(landmark.timestamp)):
            active_landmark_list.append([landmark.id, landmark.rssi[i], landmark.timestamp[i]])
            #active_landmark_list.append([landmark.id, landmark.max_rssi, landmark.max_time])
    product_list = []
    for product in products:
        for i  in range(len(product.rssi)):
            product_list.append([product.item_no, product.id, product.rssi[i], product.timestamp[i], product.actual_landmark_id])
            #product_list.append([product.id, product.max_rssi, product.max_time,product.actual_landmark_id])

    landmark_list = []
    for landmark in passive_landmarks:
        for i in range(0, len(landmark.timestamp)):
            landmark_list.append([landmark.id, landmark.rssi[i], landmark.timestamp[i]])


    # active_landmark_predict_list = []
    # for landmark in landmarks:
    #     for i in range(0, len(landmark.timestamp)):
    #         active_landmark_predict_list.append([landmark.id, landmark.rssi[i], landmark.timestamp[i]])
    #         #active_landmark_list.append([landmark.id, landmark.max_rssi, landmark.max_time])
    # product_predict_list = []
    # for product in products:
    #     for i  in range(len(product.rssi)):
    #         #product_list.append([product.id, product.max_rssi[i], product.max_time[i], product.actual_landmark_id])
    #         product_predict_list.append([product.id, product.max_rssi, product.max_time, product.item_no])

    with open('Products.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(product_list)
    with open('Active_Landmarks.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(active_landmark_list)

    with open('Landmarks.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(landmark_list)

    # with open('Products_predict.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(product_predict_list)
    # with open('Active_Landmarks_predict.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(active_landmark_predict_list)
    # with open('Passive_Landmarks.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(landmark_list)


def plot_rssi(products, landmarks):
    for product in products:
        plt.plot(product.max_time, product.max_rssi, marker = 'o', markersize=5, color=product.color)
    i=0
    for landmark in landmarks:
        landmark.color = colors[i%8]
        plt.plot(landmark.max_time, landmark.max_rssi, marker = 'o', markersize=10, color=colors[i%8])
        i+=1
    plt.show()

def main():
    result = animation()
    products = result[0]
    landmarks = result[1]
    passive_landmarks = result[2]
    sections = result[3]

    color_dict = {}
    for landmark in landmarks:
        color_dict[landmark.id] = landmark.color

    print(color_dict)
    calculate_rssi(products)
    calculate_rssi(landmarks)
    calculate_rssi(passive_landmarks)
    write_data(passive_landmarks, landmarks, products)
    products = run_model(products, passive_landmarks, landmarks, color_dict)

    #plot_rssi_time(products, landmarks, passive_landmarks)
    # prediction_products = predictions()
    # item_dict = {}
    # for i in range(len(prediction_products)):
    #     item_dict[prediction_products[1]] = prediction_products[-1]
    # for product in products:
    #     product.predicted_landmark_id = item_dict[product.item_no]
    #     product.set_color(product.predicted_landmark_id )
    

    #plot_rssi(products, landmarks)
    #K_Means_Clustering(landmarks, products)
    result_renderer(products, landmarks, sections)

if __name__ == '__main__':
    main()