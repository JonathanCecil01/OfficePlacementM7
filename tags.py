import pygame
import random
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
    def draw(self, screen, color):
        pygame.draw.circle(screen, color, self.location, 10)
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
        self.max_rssi = -81
        self.timestamp_range = []

    def find_max_rssi(self):
        pass


class LandMark(Tag):
    def __init__(self, id, location):
        Tag.__init__(self, location)
        self.id = id
        self.timestamp = []
        self.rssi = []
        self.distances  = []
        self.max_rssi = -81
        self.timestamp_range = []
    
    def find_max_rssi(self):
        pass

landmarks = []
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# screen.fill((255, 255, 255))

# def plot_Landmarks(count):
#     steps_x  = SCREEN_WIDTH/5
#     steps_y  = SCREEN_HEIGHT/2
#     loc = [200,250]
#     flag = True
#     for i in range(count-1):
#         l = LandMark("L"+str(i), loc)
#         l.draw()
#         landmarks.append(l)
#         if i%2==0:
#             loc[0]+=steps_x
#         if i%2!=0:
#             if flag:
#                 loc[1]+=steps_y
#                 flag = False
#             else:
#                 loc[1]-=steps_y
#                 flag = True
#     for landmark in landmarks:
#         print(landmark.location)
#         landmark.draw()



# flag = True
# i = 5



# while flag:
#     plot_Landmarks(10)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             flag = False
#             break
#     pygame.display.update()
#     i+=1