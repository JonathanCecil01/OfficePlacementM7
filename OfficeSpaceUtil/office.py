import matplotlib.pyplot as plt
import pygame
from tags import LandMark, Product, Reader, ActiveLandMark
from copy import deepcopy
import random
import math
import datetime

#define the basic parameters
ScreenWidth = 1000
ScreenHeight = 1000
Product_tag_count = 500
Count = 10
product_types = 10

class Sections:         #Splitting the office regionm into sections
    def __init__(self, left, top, width, height):
        self.left = left    #left of the only two defined points of the sector (rectangl)
        self.top = top      #top coordinate of the sector (rectangl)
        self.width = width  
        self.height = height
        self.location_id = None
        self.products = []  #products inside the rectangle
        self.landmarks = [] #location tags that correspond to the sector
        self.colour = None

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (self.left, self.top, self.width, self.height), 3) #rectangles of defined width and height for office space


class Office:  #the entire game object defining the terrain
    def __init__(self, reader:Reader):
        pygame.init()
        self.reader = reader
        self.product_types = product_types
        self.N = Product_tag_count
        self.SCREEN_WIDTH = ScreenWidth
        self.SCREEN_HEIGHT = ScreenHeight
        self.COUNT = Count
        self.sections = []
        self.active_landmarks = []
        self.passive_landmarks = []
        self.products = []
        self.predicted_products = []
        self.colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"] # color values for the 8 locations
         #initial start of the pygame screen with white background

    def draw_screen(self):
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screen.fill((255, 255, 255))



    def plot_sections(self):   #plotting the sections in the pygame window
        step_x= self.SCREEN_WIDTH/(self.COUNT/2)
        step_y = self.SCREEN_HEIGHT/2
        start_x = 125
        start_y = 125
        for i in range(4):
            s = Sections(start_x, start_y, 100, 250)
            s.draw(self.screen)
            self.sections.append(s)
            start_x = start_x + step_x
            s.colour = self.colors[i%8]  #defining the colour for each section
        start_x = 125
        start_y += step_y
        for i in range(4):
            s = Sections(start_x, start_y, 100, 250)
            s.draw(self.screen)
            self.sections.append(s)
            start_x = start_x + step_x
            s.colour = self.colors[i%8 + 4]



    def plot_Active_Landmarks(self): #plotting the active landmarks
        surface = pygame.Surface((self.SCREEN_WIDTH,self.SCREEN_HEIGHT), pygame.SRCALPHA)
        i =0 
        for section in self.sections:
            l = ActiveLandMark("L"+str(i), [section.left+int(section.width/2), section.top+int(section.height/2) ], 50, "0000AL"+str(i)) #Initializing the active landmarks
            l.color =  section.colour
            self.active_landmarks.append(l)
            i+=1
        i = 0
        for landmark in self.active_landmarks:
            self.sections[i].location_id  = landmark.id  #setting the location id for each sector along with the landmark
            landmark.draw(surface, landmark.color, 10)
            pygame.display.update()
            i+=1
        self.screen.blit(surface,  (0, 0))

    def plot_Landmarks(self):   #plotting the passive landmarks in every sector
        for section in self.sections:    # 4 passive lanmarks around each sector
            l1 = LandMark(section.location_id + "L0", [section.left+int(section.width/2), section.top - int(section.height/8)], "0000B"+section.location_id+"L0")
            l2 = LandMark(section.location_id + "L1", [section.left - int(section.width/4), section.top+int(section.height/2)],"0000B"+section.location_id+"L1")
            l3 = LandMark(section.location_id + "L2", [section.left+int(section.width/2), section.top + section.height + int(section.height/8)],"0000B"+section.location_id+"L2")
            l4 = LandMark(section.location_id + "L3", [section.left + section.width+int(section.width/4), section.top + int(section.height/2)],"0000B"+section.location_id+"L3")
            section.corners = [l1, l2, l3, l4]
            for landmark in section.corners:
                landmark.color = section.colour
                landmark.draw(self.screen, section.colour, 8)
        for section in self.sections:
            for corner in section.corners:
                self.passive_landmarks.append(corner)


    def plot_products(self):    #plotting products around the given section
        item_no_i = 0
        iterations= int(self.N/ len(self.sections))   #equally distributing the total number of products in each sector
        for section in self.sections:
            for i in range(iterations):
                location = [random.randint(section.left, section.left + section.width), random.randint(section.top, section.top + section.height)]
                product  = Product("P"+str(random.randint(0, self.product_types)), location, section.location_id, "303A"+str(item_no_i))
                product.color = 'green'#section.colour
                section.products.append(product)
                self.products.append(product)
                item_no_i+=1
        for product in self.products:
            product.draw(self.screen, "green", 5) #plotting the prodcuts in the screen

    def calculate_rssi(self):       #function to call the rssi calculation in each tag
        for tag in self.products:
            tag.calc_rssi()
        for tag in self.active_landmarks:
            tag.calc_rssi()
        for tag in self.passive_landmarks:
            tag.calc_rssi()
        return

    def result_renderer(self): #Final animation after the prediction 
        flag = True
        screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        screen.fill((255, 255, 255))
        surface = pygame.Surface((self.SCREEN_WIDTH,self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for section in self.sections:
            section.draw(screen)
        for product in self.predicted_products:
            product.draw(screen, product.color, 5)
        for landmark in self.active_landmarks:
            landmark.draw(surface, landmark.color, 10)
        for landmark in self.passive_landmarks:
            landmark.draw(surface, landmark.color, 10)
        screen.blit(surface, (0, 0))
        while flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False
                    break
            pygame.display.update()
        return


    def animation(self):        #initial animation with reader for data generation.
        self.draw_screen()
        self.plot_sections()#plotting sections
        self.plot_Active_Landmarks()#plotting landmarks
        self.plot_Landmarks()    #plotting the passive landmarks
        self.plot_products()  #plotting products

        flag = True             #flag for Running Animation
        i = 5
        #self.reader = Reader([0, 0], 30) #creating the reader with the values

        top_surface = pygame.Surface((self.SCREEN_WIDTH,self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.reader.draw(top_surface, 0)    
        self.screen.blit(top_surface, (0, 0))

        rotation_angle = 0

        start_time = datetime.datetime.now() #start timestamp to calculate the time difference for timestamp
        while flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False
                    break
                if event.type == pygame.KEYDOWN: #movement of the reader controlled by W,A,S,D keys each step is scalled down to the movement of an average human
                    if event.key == pygame.K_s:
                        self.reader.location[1]+=38
                    if  event.key == pygame.K_a:
                        self.reader.location[0]-=38
                    if event.key == pygame.K_d:
                        self.reader.location[0]+=38
                    if event.key == pygame.K_w:
                        self.reader.location[1]-=38
                    if event.key == pygame.K_e:  # Rotate clockwise (increase angle)
                        rotation_angle += 45
                        self.reader.image = pygame.transform.rotate(self.reader.image, rotation_angle)
                    if event.key == pygame.K_q:  # Rotate counterclockwise (decrease angle)
                        rotation_angle -= 45 
                        self.reader.image = pygame.transform.rotate(self.reader.image, rotation_angle)
                    top_surface.fill((255, 255, 255, 0))
                    self.reader.draw(top_surface, rotation_angle)
                    self.screen.blit(top_surface, (0, 0))
            temp_products = []
            temp_landmarks = []
            temp_passive_landmarks = []
            for product in self.products: # data generation for the products in the readable range
                if math.dist(product.location, self.reader.location)<=self.reader.radius:
                    product.distances.append(math.dist(product.location, self.reader.location))
                    temp_products.append(product)
            for landmark in self.active_landmarks:#data generation for the landmarks in the readable range
                if math.dist(landmark.location, self.reader.location)<=self.reader.radius:
                    landmark.distances.append(math.dist(landmark.location, self.reader.location)) #appending the distance
                    temp_landmarks.append(landmark)
            for landmark in self.passive_landmarks: #data generation for the passive landmarks 
                if math.dist(landmark.location, self.reader.location)<=self.reader.radius: #an apprx range of 2m for the reader 
                    landmark.distances.append(math.dist(landmark.location, self.reader.location))
                    temp_passive_landmarks.append(landmark)


            c_time = datetime.datetime.now() #calculating current time
            delta = c_time - start_time
            sec = delta.total_seconds()*1000 #difference in time stamp from start to now in miliseconds
            for product in temp_products:   #appending the time stamp
                product.start_timestamp = start_time
                product.timestamp.append(c_time)
            for landmark in temp_landmarks:
                landmark.start_timestamp = start_time
                landmark.timestamp.append(c_time)
            for landmark in temp_passive_landmarks:
                landmark.start_timestamp = start_time
                landmark.timestamp.append(c_time)

            pygame.display.flip()
            i+=1
        #return [products, landmarks, passive_landmarks, sections, reader]   #returning all the plotted values
