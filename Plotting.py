import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import csv
def read_data():
    landmarks = []
    with open('Landmarks.csv', 'r') as file:  #change to any path name where landmark data exists
        reader = csv.reader(file)
        for row in reader:
            landmarks.append(row)
    file.close()
    for landmark in landmarks:
        landmark[1] = float(landmark[1])  #converting the rssi and timestamp to float values
        landmark[2] = float(landmark[2])
    start = landmarks[0][2]
    products = []


    with open('Products.csv', 'r') as file1: #change to any path name where product data exists
        reader = csv.reader(file1)
        for row in reader:
            products.append(row) 
    for product in products:
        product[2] = float(product[2])  #converting the rssi and timestamp to float values
        product[3] = float(product[3])
        product[2] = float("{:.0f}".format(product[2]))   #removing the unnecessary precision in floating point values 
        product[3] = float("{:.0f}".format(product[3]))
    
    return [products, landmarks]


# fig = plt.figure()
# ax = plt.axes(projection='3d')

data = read_data()
products = data[0]
landmarks = data[1]
zdata = []
xdata = []
ydata = []
i = 0
for landmark in landmarks:
  xdata.append(int(landmark[0][1]))
  ydata.append(landmark[2])
  zdata.append(landmark[1])

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.scatter3D(xdata, ydata, zdata, c=zdata, cmap='Greens');
ax.view_init(45, 0);
# for landmark in landmarks:
#     ax.plot3d(int(landmark[0][1])*int(landmark[0][3]), landmark[1], landmark[2], color = 'black')
plt.show()
