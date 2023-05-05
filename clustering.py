import numpy as np
import matplotlib.pyplot as plt
# import pandas as pd
import random
import math

N  = 500 #No of reads from the RFID
T = 100 #time in minutes
iterations = 1000
data = []
for i in range(0, iterations):
    product_id = random.randint(0, N)
    time_stamp = random.randint(0, T)
    rssi = random.randint(-80, -30)
    data.append([product_id, time_stamp, rssi])

product_dictionary = {}
for entry in data:
    product_dictionary[entry[0]] = [-1, -81]
for entry in data:
    if product_dictionary[entry[0]][1]<= entry[2]:
        product_dictionary[entry[0]] = [entry[1], entry[2]]

keys = list(product_dictionary.keys())
keys.sort()
print(keys)
sorted_dictionary = {i : product_dictionary[i] for i in keys}
print(sorted_dictionary)
for i in keys:
    plt.plot(sorted_dictionary[i][0], sorted_dictionary[i][1], marker = 'o', markersize=5, color="green")

location_tags = [["L1", -1, -81], ["L2", -1, -81], ["L3", -1, -81], ["L4", -1, -81]]

for i in range(0,10):
    l1 = [random.randint(0, T), random.randint(-80, -30)]
    if location_tags[0][2]<=l1[1]:
        location_tags[0][1] = l1[0]
        location_tags[0][2] = l1[1]
    l2 = [random.randint(0, T), random.randint(-80, -30)]
    if location_tags[1][2]<=l2[1]:
        location_tags[1][1] = l2[0]
        location_tags[1][2] = l2[1]
    l3 = [random.randint(0, T), random.randint(-80, -30)]
    if location_tags[2][2]<=l3[1]:
        location_tags[2][1] = l3[0]
        location_tags[2][2] = l3[1]
    l4 = [random.randint(0, T), random.randint(-80, -30)]
    if location_tags[3][2]<=l4[1]:
        location_tags[3][1] = l4[0]
        location_tags[3][2] = l4[1]

colors = ["red", "blue", "yellow", "black"]
j = 0
for i in location_tags:
    plt.plot(i[1], i[2], marker = 'o', markersize= 7 ,color=colors[j])
    j+=1
plt.show()

for i in sorted_dictionary.keys():
    x = sorted_dictionary[i][0]
    y = sorted_dictionary[i][1]
    distance1 = math.dist([x, y], [location_tags[0][1], location_tags[0][2]])
    distance2 = math.dist([x, y], [location_tags[1][1], location_tags[1][2]])
    distance3 = math.dist([x, y], [location_tags[2][1], location_tags[2][2]])
    distance4 = math.dist([x, y], [location_tags[3][1], location_tags[3][2]])
    if min(distance1, distance2, distance3, distance4) == distance1:
        plt.plot(x, y, marker = 'o', markersize= 5 ,color=colors[0])
    elif min(distance1, distance2, distance3, distance4) == distance2:
        plt.plot(x, y, marker = 'o', markersize= 5 ,color=colors[1])
    elif min(distance1, distance2, distance3, distance4) == distance3:
        plt.plot(x, y, marker = 'o', markersize= 5 ,color=colors[2])
    elif min(distance1, distance2, distance3, distance4) == distance4:
        plt.plot(x, y, marker = 'o', markersize= 5 ,color=colors[3])
plt.show()
