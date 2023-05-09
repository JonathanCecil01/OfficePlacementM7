from office import *
from tags import *
import matplotlib.pyplot as plt

colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]


def K_Means_Clustering(landmarks, products):
    centres  = [[landmark.max_time, landmark.max_rssi] for landmark in landmarks]
    for product in products:
        distances = [math.dist([product.max_time, product.max_rssi], i) for i in centres]
        min_distance = min(distances)
        index_min = distances.index(min_distance)
        product.color = landmarks[index_min].color
        product.predicted_landamrk_id = landmarks[index_min].id
    plot_rssi(products, landmarks)    

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
    sections = result[2]
    calculate_rssi(products)
    calculate_rssi(landmarks)
    for product in products:
        product.set_max_rssi()
    for landmark in landmarks:
        landmark.set_max_rssi()
    plot_rssi(products, landmarks)
    K_Means_Clustering(landmarks, products)
    result_renderer(products, landmarks, sections)

if __name__ == '__main__':
    main()