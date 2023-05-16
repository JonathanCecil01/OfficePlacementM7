import matplotlib.pyplot as plt
import pygame
from tags import LandMark, Product, Reader, ActiveLandMark
from copy import deepcopy
import random
import math
import datetime

#define the basic parameters

pygame.init()
N = 500
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
COUNT = 10


colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"] # color values for the 8 locations
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill((255, 255, 255)) #initial start of the pygame screen with white background

class Offices(object):  #the entire game object defining the terrain
    def __init__(self, sections, landmarks, products):
        self.sections = sections
        self.landmarks = landmarks
        self.products = products

class Sections:         #Splitting the office regionm into sections
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.location_id = None
        self.products = []
        self.corners = []
        self.colour = None

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (self.left, self.top, self.width, self.height), 3) #rectangles of defined width and height for office space


def plot_sections(count):
    step_x= SCREEN_WIDTH/(count/2)
    step_y = SCREEN_HEIGHT/2
    start_x = 125
    start_y = 50
    sections = []
    for i in range(4):
        s = Sections(start_x, start_y, 150, 400)
        s.draw(screen)
        sections.append(s)
        start_x = start_x + step_x
        s.colour = colors[i%8]  #defining the colour for each section
    start_x = 125
    start_y += step_y
    for i in range(4):
        s = Sections(start_x, start_y, 150, 400)
        s.draw(screen)
        sections.append(s)
        start_x = start_x + step_x
        s.colour = colors[i%8 + 4]
    
    return sections



def plot_Active_Landmarks(count, sections):
    surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
    landmarks = []
    steps_x  = SCREEN_WIDTH/5
    steps_y  = SCREEN_HEIGHT/2
    loc1 = [200,250]
    flag = True
    i =0 
    for section in sections:
         l = ActiveLandMark("L"+str(i), [section.left+int(section.width/2), section.top+int(section.height/2) ], 50)
         landmarks.append(l)
         i+=1
    i = 0
    for landmark in landmarks:
        sections[i].location_id  = landmark.id
        landmark.draw(surface, sections[i].colour, 10)
        pygame.display.update()
        i+=1
    screen.blit(surface,  (0, 0))
    return landmarks

def plot_Landmarks(sections):
    for section in sections:
        l1 = LandMark(section.location_id + "L0", [section.left, section.top])
        l2 = LandMark(section.location_id + "L1", [section.left + section.width, section.top])
        l3 = LandMark(section.location_id + "L2", [section.left, section.top + section.height])
        l4 = LandMark(section.location_id + "L3", [section.left + section.width, section.top + section.height])
        section.corners = [l1, l2, l3, l4]
        for landmark in section.corners:
            landmark.draw(screen, section.colour, 8)
    passive_landmarks = []
    for section in sections:
        for corner in section.corners:
            passive_landmarks.append(corner)
    return passive_landmarks

    
def plot_products(sections):
    products = []
    count = 1000
    item_no_i = 0
    iterations= int(count/ len(sections))
    for section in sections:
        for i in range(iterations):
            location = [random.randint(section.left, section.left + section.width), random.randint(section.top, section.top + section.height)]
            product  = Product("P"+str(random.randint(0, N)), location, section.location_id, item_no_i)
            section.products.append(product)
            products.append(product)
            item_no_i+=1
    for product in products:
        product.draw(screen, "green", 5)
    return products

def calculate_rssi(tags):
    for tag in tags:
        tag.calc_rssi()
    return

def result_renderer(products, landmarks, sections):
    flag = True
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))
    surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
    for section in sections:
        section.draw(screen)
    for product in products:
        product.draw(screen, product.color, 5)
    for landmark in landmarks:
        landmark.draw(surface, landmark.color, 10)
    screen.blit(surface, (0, 0))
    while flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                flag = False
                break
        pygame.display.update()
    return


def animation():
    sections = plot_sections(COUNT)
    landmarks = plot_Active_Landmarks(COUNT, sections)#
    passive_landmarks = plot_Landmarks(sections)
    flag = True
    i = 5
    products = plot_products(sections)
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
        temp_products = []
        temp_landmarks = []
        temp_passive_landmarks = []
        for product in products:
            if math.dist(product.location, reader.location)<=200:
                product.distances.append(math.dist(product.location, reader.location))
                temp_products.append(product)
        for landmark in landmarks:
            if math.dist(landmark.location, reader.location)<=200:
                landmark.distances.append(math.dist(landmark.location, reader.location))
                temp_landmarks.append(landmark)
            else:
                landmark.distances.append(999999)
                temp_landmarks.append(landmark)
        for landmark in passive_landmarks:
            if math.dist(landmark.location, reader.location)<=200:
                landmark.distances.append(math.dist(landmark.location, reader.location))
                temp_passive_landmarks.append(landmark)
            else:
                landmark.distances.append(999999)
                temp_passive_landmarks.append(landmark)

        c_time = datetime.datetime.now()
        delta = c_time - start_time
        sec = delta.total_seconds()*1000
        for product in temp_products:
            product.timestamp.append(sec)
        for landmark in temp_landmarks:
            landmark.timestamp.append(sec)
        for landmark in temp_passive_landmarks:
            landmark.timstamp.append(sec)

        pygame.display.flip()
        i+=1
    return [products, landmarks, passive_landmarks, sections]
