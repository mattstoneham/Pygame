__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *
import numpy as np


# global variables
SCRIPTPATH = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
SPRITEPATH = SCRIPTPATH + '\sprites'
GameState = 'menu screen'


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

    # global variables
    global GameState, SPRITEPATH

    # resources
    ShipSprite = pygame.image.load(SPRITEPATH+'/player.png')

    # class properties
    Type = 'Player'
    Draw = False
    State = 'Inactive'
    PlayerName = ''
    Score = 0
    Lives = 3
    Position = [0, 0]
    Orientation = 0
    Vector = np.array([0, 0])
    ThrustVector = np.array([0, 0])


    # static properties
    THRUST_V_LENGTH = 1  # the vector length of a thrust impulse
    ROTATION_STEP = 1  # the step value (per frame) of a rotation
    DECAY_RATE = 1  # decay rate (as a percentage) of the movement vector



    def __init__(self, SpawnLocation):  # class constructor
        self.spawn(SpawnLocation)
        pass

    def spawn(self, SpawnLocation):  # spawns a new player ship
        print('spawning new player ship at position {0}'.format(SpawnLocation))
        self.Position = SpawnLocation
        self.Orientation = 0
        self.Draw = True
        self.State = 'Active'
        pass

    def explode(self):  # triggered if collision between player and asteroid
        self.State = 'Exploding'
        self.Draw = False  # set flag so ship isn't drawn until re-spawned
        self.Lives -= 1
        if self.Lives == 0:
            GameState = 'game over'

    def rotate_cw(self):
        pass

    def rotate_ccw(self):
        pass

    def thrust(self):
        # build the thrust vector
        pass

    def update_position(self):
        # decay the main vector
        # add the thrust vector to the main vector
        # generate new player position from main vector
        pass



class Explosion():

    # global variables
    global GameState, SPRITEPATH

    # resources
        # explosion sprites here

    # class properties
    Type = 'Asteroid'
    Draw = False

    def __init__(self, SpawnLocation):  # class constructor
        pass


class Asteroid():

    # global variables
    global GameState, SPRITEPATH

    # resources
        # explosion sprites here

    # class properties
    Type = 'Asteroid'
    Draw = False

    def __init__(self):  # class constructor
        pass


class Projecile():

    # global variables
    global GameState, SPRITEPATH

    # resources
        # explosion sprites here

    # class properties
    Type = 'Asteroid'
    Draw = False

    def __init__(self):  # class constructor
        pass






def main(): # main game code

    pygame.init()
    # some constants...
    FPS = 60 # set frames per second

    # keyboard mappings
    INPUT_ROTATE_CCW = 'left_arrow'
    INPUT_ROTATE_CW = 'right_arrow'
    INPUT_THRUST = 'up_arrow'
    INPUT_FIRE = 'space'

    fpsClock = pygame.time.Clock()
    window = Window(CAPTION='player movement test')  # instance a window for the game


    player = Player(window.center())  # instance a player at centre of window
    object_list = {'Asteroids':[], 'Players':[player], 'Explosions':[]}  # dic of all the active objects

    while True: # main game loop

        # Event handling loop
        for event in pygame.event.get():

            # collision event check and handling
            # if player/asteroid collide detected
                # player.Explode()
                # spawn an explosion

            if player.State == 'Active':  # only accept player inputs if ship is active
                # player input event handling
                    # if left arrow rotate ccw

                    # if right arrow rotate cw

                    # if space modify the thrust vector

                    # if fire, spawn a projectile
                pass

            # update object positions
            player.update_position()


            # draw objects
            window.DISPLAYSURF.fill(0, 0, 0)
            for asteroid in object_list['Asteroids']:
                # if asteroid.Draw(): blit asteroid at asteroid.Postion
                pass

            for player in object_list['Players']:
                # if player.Draw(): blit player sprite at player.Postion
                pass


            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        fpsClock.tick(FPS)


if __name__ == '__main__':
    main()
