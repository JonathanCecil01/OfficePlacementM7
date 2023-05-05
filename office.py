import matplotlib.pyplot as plt
import pygame

pygame.init()

screen = pygame.display.set_mode((400, 500))
screen.fill((255, 255, 255))

flag = True
i = 5
while flag:
    pygame.draw.rect(screen, (0, 0+i, 255),(200,150,100,50))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
            break
    pygame.display.update()
    i+=1
