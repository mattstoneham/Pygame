__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *

pygame.init()

FPS = 30 # set frames per second
fpsClock = pygame.time.Clock()

# set up window
DISPLAYSURF = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('Animation')

# custom colours
WHITE = (255, 255, 255)

# script and resource locations
basePath = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
spritePath = basePath + '\sprites'

# load sprites
catImage = pygame.image.load(spritePath+'\caticorn.png')
catx = 10
caty = 10
direction = 'right'

while True: # main game loop
    DISPLAYSURF.fill(WHITE)

    if direction == 'right':
        catx += 5
        if catx == 280:
            direction = 'down'

    if direction == 'down':
        caty += 5
        if caty == 220:
            direction = 'left'

    if direction == 'left':
        catx -= 5
        if catx == 10:
            direction = 'up'

    if direction == 'up':
        caty -= 5
        if caty == 10:
            direction = 'right'

    DISPLAYSURF.blit(catImage, (catx, caty))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)