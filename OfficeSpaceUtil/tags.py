import pygame
import random
import math

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

PATH_LOSS_EXPONENT = 2
colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]



class Reader:       #The reader class to emulate the RFID Reader
    def __init__(self, location : list, session = 0, rxpower = 30, queue = 4): #radius defines the range of the reader
        self.location = location
        self.session = session
        self.rxpower = rxpower
        self.queue = queue
        self.range_centre = []
        self.circle_rad = 45
        #load image
        self.image = pygame.image.load("OfficeSpaceUtil/images/rfid_reader.png")
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.calc_radius()

    def calc_radius(self):
        factor = 10 - self.rxpower/3
        self.radius = 100/(2**factor)
   
    def draw(self, surface, angle):
        pygame.draw.circle(surface , (30,224,33,20), self.location, self.radius) #drawing the radius of the reader
        image_rect = self.image.get_rect(center=self.location)
        self.range_centre = [image_rect.x + 3*image_rect.w/2, image_rect.y]
        surface.blit(self.image, image_rect)



class Tag:          #the super class Tag for both the prduct and location tags
    def __init__(self, location, item_no):
        self.location = location
        self.start_timestamp = 0
        self.item_no = item_no
    def draw(self, screen, color, radius):
        pygame.draw.circle(screen, color, self.location, radius) #general draw function
        pygame.display.update()
        return
    

class Product(Tag):     #the class for the Product tag
    def __init__(self, id, location, landmark_id, item_no):
        Tag.__init__(self, location, item_no)    #deriving from the Tag class
        self.id = id        #id of the product
        self.rssi_A = -45   #rssi value of the tag at 1m distance from the reader
        self.timestamp = [] #set of timestamps for the value sread by the tag
        self.distances = [] #distances from the reader crrosponding to the timestamps
        self.rssi = []      #a list to calculate and store the rssi value
        self.max_rssi = -91 #set to the minimum rssi value that  can be reached
        self.max_time= 0    #to store the time at which tag reached the max
        self.color = "green"    #initial color of the product before classification
        self.actual_landmark_id = landmark_id #actual id used for testing the NN's accuracy
        self.predicted_landmark_ids = []    #set of predicted landmarks for each timestamp 
        self.predicted_landmark_id = None   #finally predicted and selected landmark id 
        #self.item_no = item_no  #unique identifier for the product
        self.set_color()

    def set_max_rssi(self): #sets the maximum rssi value and the corresponding time stamp
        self.max_rssi = max(self.rssi)
        index = self.rssi.index(self.max_rssi)
        self.max_time = self.timestamp[index]

    def calc_rssi(self):    #calculates the rssi value with distance
        for i in range(0, len(self.timestamp)):
            self.rssi.append(self.rssi_A - 10*PATH_LOSS_EXPONENT*math.log10(self.distances[i])) # A - 10*n*log(d) where n is path loss exponenet
    
    def set_color(self):    #setting the color of the tag w.r.t actual landmark
        index = int(self.actual_landmark_id[-1])
        self.color = colors[index]
        


class LandMark(Tag):    #class for LandMark Tag 
    def __init__(self, id, location, item_no):
        Tag.__init__(self, location, item_no) #deriing property from the Tag class
        self.id = id    #unique id for the location
        self.timestamp = [] #set of timestamps where the location tag is read
        self.rssi = []  #set of corresponding rssi values for the timestamp
        self.rssi_A = -30   #rssi value at 1m distance from the reader
        self.distances  = []    #set of distances used to calculate the rssi value 
        self.max_rssi = -91 #set to minimum readable
        self.max_time = 0   #time at which max is reached (used in clustering)
        self.color = "black" 

    def set_max_rssi(self): #seetting max rssi value
        self.max_rssi = max(self.rssi)
        index = self.rssi.index(self.max_rssi)
        self.max_time = self.timestamp[index]

    def calc_rssi(self):    #calculating the rssi value
        for i in range(0, len(self.timestamp)):
            if self.distances[i] == 999999:
                self.rssi.append(-91)
            else:
                self.rssi.append(self.rssi_A - 10*PATH_LOSS_EXPONENT*math.log10(self.distances[i]))

class ActiveLandMark(LandMark):     #active landmark tag which is stronger 
    def __init__(self, id, location, range, item_no):
        LandMark.__init__(self, id, location, item_no) #derives from the LandMark tag class
        self.rssi_A = -30
        self.range = range

    def draw(self, surface, color, radius): #seperate draw function for different style
        pygame.draw.circle(surface , (224,30,33,20), self.location, self.range)
        pygame.draw.circle(surface, color, self.location, radius)
        return
