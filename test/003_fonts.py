__author__ = 'Matt'

import pygame, sys
from pygame.locals import *

pygame.init()
DISPLAYSURF = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Hello World')

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

fontObj = pygame.font.Font('freesansbold.ttf', 32)  # create a font object
textSurfaceObj = fontObj.render('Hello World!', True, GREEN, BLUE) # create surface obj with text drawn on it
textRectObj = textSurfaceObj.get_rect() # create a rect obj from the surface obj
textRectObj.center = (200, 150)

while True: # main game loop
    DISPLAYSURF.fill(WHITE)
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()


