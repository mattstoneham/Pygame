__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *



class Window():

    DISPLAYSURF = ''
    WINDOWSIZE=(800, 600)
    CAPTION = 'your caption here'

    def __init__(self, WINDOWSIZE=WINDOWSIZE, CAPTION=CAPTION): # class constructor
        self.DISPLAYSURF = pygame.display.set_mode(WINDOWSIZE, 0, 32)
        pygame.display.set_caption(CAPTION)

    def center(self):
        return (int(self.WINDOWSIZE[0] / 2), int(self.WINDOWSIZE[1] / 2))


class Player():

    LIVES = 3
    POSITION = ()

    def __init__(self): # class constructor
        pass




def main(): # main game code

    pygame.init()
    # some constants...
    FPS = 60 # set frames per second
    fpsClock = pygame.time.Clock()
    thisWindow = Window(CAPTION='player movement test')




    while True: # main game loop

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        fpsClock.tick(FPS)


if __name__ == '__main__':
    main()
