import pygame
import random
import math
# pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

PATH_LOSS_EXPONENT = 2
colors = ["red", "blue", "brown", "black", "purple", "yellow", "pink", "orange"]



class Reader:
    def __init__(self, location, radius):
        self.location = location
        self.radius = radius
    
    def draw(self, surface):
        pygame.draw.circle(surface , (30,224,33,20), self.location, 100)
        pygame.draw.circle(surface, "black", self.location, 5)

class Tag:
    def __init__(self, location):
        self.location = location
    def draw(self, screen, color, radius):
        pygame.draw.circle(screen, color, self.location, radius)
        pygame.display.update()
        return
    

class Product(Tag):
    def __init__(self, id, location, landmark_id, item_no):
        Tag.__init__(self, location)
        self.id = id
        self.rssi_A = -45
        self.timestamp = []
        self.distances = []
        self.rssi = []
        self.max_rssi = -91
        self.max_time= 0
        self.color = "green"
        self.actual_landmark_id = landmark_id
        self.predicted_landmark_ids = []
        self.predicted_landmark_id = None
        self.item_no = item_no
        self.set_color()

    def set_max_rssi(self):
        self.max_rssi = max(self.rssi)
        index = self.rssi.index(self.max_rssi)
        self.max_time = self.timestamp[index]

    def calc_rssi(self):
        for i in range(0, len(self.timestamp)):
            self.rssi.append(self.rssi_A - 10*PATH_LOSS_EXPONENT*math.log10(self.distances[i]))
    
    def set_color(self):
        index = int(self.actual_landmark_id[-1])
        self.color = colors[index]
        


class LandMark(Tag):
    def __init__(self, id, location):
        Tag.__init__(self, location)
        self.id = id
        self.timestamp = []
        self.rssi = []
        self.rssi_A = -30
        self.distances  = []
        self.max_rssi = -91
        self.max_time = 0
        self.color = "black"

    def set_max_rssi(self):
        self.max_rssi = max(self.rssi)
        index = self.rssi.index(self.max_rssi)
        self.max_time = self.timestamp[index]

    def calc_rssi(self):
        for i in range(0, len(self.timestamp)):
            if self.distances[i] == 999999:
                self.rssi.append(-91)
            else:
                self.rssi.append(self.rssi_A - 10*PATH_LOSS_EXPONENT*math.log10(self.distances[i]))

class ActiveLandMark(LandMark):
    def __init__(self, id, location, range):
        LandMark.__init__(self, id, location)
        self.rssi_A = -30
        self.range = range

    def draw(self, surface, color, radius):
        pygame.draw.circle(surface , (224,30,33,20), self.location, self.range)
        pygame.draw.circle(surface, color, self.location, radius)
        return
