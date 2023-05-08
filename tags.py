import pygame
import random
import math
# pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

PATH_LOSS_EXPONENT = 2
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# screen.fill((255, 255, 255))

class Reader:
    def __init__(self, location, radius):
        self.location = location
        self.radius = radius
    
    def draw(self, surface):
        pygame.draw.circle(surface , (30,224,33,20), self.location, 250)
        # screen.blit(surface, (0, 0))
        pygame.draw.circle(surface, "black", self.location, 5)
        #pygame.display.update()

class Tag:
    def __init__(self, location):
        self.location = location
    def draw(self, screen, color, radius):
        pygame.draw.circle(screen, color, self.location, radius)
        pygame.display.update()
        return
    

class Product(Tag):
    def __init__(self, id, location):
        Tag.__init__(self, location)
        self.id = id
        self.rssi_A = random.randint(-90,-30)
        self.timestamp = []
        self.distances = []
        self.rssi = []
        self.max_rssi = -91
        self.timestamp_range = []
        self.max_time= 0
        self.color = "green"

    def set_max_rssi(self):
        self.max_rssi = max(self.rssi)
        index = self.rssi.index(self.max_rssi)
        self.max_time = self.timestamp[index]

    def calc_rssi(self):
        for i in range(0, len(self.timestamp)):
            self.rssi.append(self.rssi_A - 10*PATH_LOSS_EXPONENT*math.log(self.distances[i]/10))


class LandMark(Tag):
    def __init__(self, id, location):
        Tag.__init__(self, location)
        self.id = id
        self.timestamp = []
        self.rssi = []
        self.rssi_A = random.randint(-50,-30)
        self.distances  = []
        self.max_rssi = -91
        self.timestamp_range = []
        self.max_time = 0
        self.color = "black"

    def set_max_rssi(self):
        self.max_rssi = max(self.rssi)
        index = self.rssi.index(self.max_rssi)
        self.max_time = self.timestamp[index]

    def calc_rssi(self):
        for i in range(0, len(self.timestamp)):
            self.rssi.append(self.rssi_A - 10*PATH_LOSS_EXPONENT*math.log(self.distances[i]/5))

class ActiveLandMark(LandMark):
    def __init__(self, id, location, range):
        LandMark.__init__(self, id, location)
        self.range = range

    def draw(self, surface, screen, color, radius):
        pygame.draw.circle(surface , (224,30,33,20), self.location, 150)
        #screen.blit(surface, (0, 0))
        pygame.draw.circle(surface, color, self.location, radius)
        #pygame.display.update()
        return
