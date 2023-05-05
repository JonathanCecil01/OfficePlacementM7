import matplotlib.pyplot as plt
import pygame
from tags import LandMark, Product, Reader
from copy import deepcopy
import random
import math
import datetime

pygame.init()
N = 100
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
COUNT = 10


colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill((255, 255, 255))

def plot_Landmarks(count):
    landmarks = []
    steps_x  = SCREEN_WIDTH/5
    steps_y  = SCREEN_HEIGHT/2
    loc1 = [200,250]
    flag = True
    for i in range(count-1):
        loc = deepcopy(loc1)
        l = LandMark("L"+str(i), loc)
        landmarks.append(l)
        if i%2==0 and i!=0:
            loc1[0]+=steps_x
        if i%2!=0:
            if flag:
                loc1[1]+=steps_y
                flag = False
            else:
                loc1[1]-=steps_y
                flag = True
    landmarks.pop(0)
    i = 0
    for landmark in landmarks:
        landmark.draw(screen, colors[i%8])
        i+=1
    return landmarks

def plot_products():
    products = []
    iterations= 100
    for i in range(iterations):
        i = random.randint(0, 1)
        if i == 1:
            location = [random.randint(150, 850), random.randint(150, 450)]
        else:
            location = [random.randint(150, 850), random.randint(600, 850)]
        product  = Product("P"+str(random.randint(0, N)), location)
        
        products.append(product)
    for product in products:
        product.draw(screen, "green")
    return products

def calculate_rssi(tags):
    for tag in tags:
        tag.calc_rssi()
    return


def Animation():
    flag = True
    i = 5
    distance_products = []
    distance_landmarks = []
    products = plot_products()
    landmarks = plot_Landmarks(COUNT)
    reader = Reader([0, 0], 30)
    top_surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
    reader.draw(top_surface)
    screen.blit(top_surface, (0, 0))
    start_time = datetime.datetime.now()
    while flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                flag = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    reader.location[1]+=100
                if  event.key == pygame.K_a:
                    reader.location[0]-=100
                if event.key == pygame.K_d:
                    reader.location[0]+=100
                if event.key == pygame.K_w:
                    reader.location[1]-=100
                top_surface.fill((255, 255, 255, 0))
                reader.draw(top_surface)
                screen.blit(top_surface, (0, 0))
        for product in products:
            if math.dist(product.location, reader.location)<=200:
                c_time = datetime.datetime.now()
                delta = c_time - start_time
                sec = delta.total_seconds()
                product.timestamp.append(sec)
                product.distances.append(math.dist(product.location, reader.location))
        for landmark in landmarks:
            if math.dist(landmark.location, reader.location)<=200:
                c_time = datetime.datetime.now()
                delta = c_time - start_time
                sec = delta.seconds
                landmark.timestamp.append(sec)
                landmark.distances.append(math.dist(landmark.location, reader.location))
        pygame.display.flip()
        i+=1
    return [products, landmarks]

