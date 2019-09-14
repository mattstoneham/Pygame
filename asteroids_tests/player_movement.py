__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *
import numpy as np


# global variables
GAMEDIR = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
SPRITEDIR = os.path.join(GAMEDIR, 'sprites')
GameState = 'menu screen'


class Window():

    DISPLAYSURF = ''
    WINDOWSIZE=(1200, 900)
    CAPTION = 'your caption here'

    def __init__(self, WINDOWSIZE=WINDOWSIZE, CAPTION=CAPTION): # class constructor
        self.DISPLAYSURF = pygame.display.set_mode(WINDOWSIZE, 0, 32)
        pygame.display.set_caption(CAPTION)

    def get_center(self):
        return (int(self.WINDOWSIZE[0] / 2), int(self.WINDOWSIZE[1] / 2))


class Player(pygame.sprite.Sprite):

    # global variables
    global GameState, SPRITEDIR

    # class properties
    type = 'Player'
    draw = False
    state = 'Inactive'
    player_name = ''
    score = 0
    lives = 3
    position = [0, 0]
    orientation = 0
    vector = np.array([0, 0])
    thrust_vector = np.array([0, 0])


    # static properties
    THRUST_V_LENGTH = 1  # the vector length of a thrust impulse
    ROTATION_STEP = 1  # the step value (per frame) of a rotation
    DECAY_RATE = 1  # decay rate (as a percentage) of the movement vector



    def __init__(self, window):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class
        self.image = pygame.image.load(os.path.join(SPRITEDIR, 'player.png')).convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = window.get_center()

        pass

    def spawn(self, SpawnLocation):  # spawns a new player ship
        print('spawning new player ship at position {0}'.format(SpawnLocation))
        self.position = SpawnLocation
        self.orientation = 0
        self.draw = True
        self.state = 'Active'
        pass

    def explode(self):  # triggered if collision between player and asteroid
        self.state = 'Exploding'
        self.draw = False  # set flag so ship isn't drawn until re-spawned
        self.lives -= 1
        if self.lives == 0:
            GameState = 'game over'

    def rotate_cw(self):
        pass

    def rotate_ccw(self):
        pass

    def thrust(self):
        # build the thrust vector
        pass

    def update(self):
        # decay the main vector
        # add the thrust vector to the main vector
        # generate new player position from main vector
        pass



class Explosion(pygame.sprite.Sprite):

    # global variables
    global GameState, SPRITEDIR

    # resources
        # explosion sprites here

    # class properties
    Type = 'Asteroid'
    Draw = False

    def __init__(self, SpawnLocation):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class


class Asteroid(pygame.sprite.Sprite):

    # global variables
    global GameState, SPRITEDIR

    # resources
        # explosion sprites here

    # class properties
    Type = 'Asteroid'
    Draw = False

    def __init__(self):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class


class Projecile(pygame.sprite.Sprite):

    # global variables
    global GameState, SPRITEDIR

    # resources
        # explosion sprites here

    # class properties
    Type = 'Asteroid'
    Draw = False

    def __init__(self):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class






def main(): # main game code

    pygame.init()
    # some constants...
    FPS = 60 # set frames per second

    # keyboard mappings
    INPUT_ROTATE_CCW = 'left_arrow'
    INPUT_ROTATE_CW = 'right_arrow'
    INPUT_THRUST = 'up_arrow'
    INPUT_FIRE = 'space'

    clock = pygame.time.Clock()
    window = Window(CAPTION='player movement test')  # instance a window for the game
    player = Player(window)
    all_sprites = pygame.sprite.Group()  # all sprites are now in this group, makes update and draw easy!
    all_sprites.add(player)
    
    while True: # main game loop
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():

            # collision event check and handling
            # if player/asteroid collide detected
                # player.Explode()
                # spawn an explosion


            #if player.State == 'Active':  # only accept player inputs if ship is active
                # player input event handling
                    # if left arrow rotate ccw

                    # if right arrow rotate cw

                    # if space modify the thrust vector

                    # if fire, spawn a projectile
                #pass

            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        # Update
        all_sprites.update()


        # Draw
        window.DISPLAYSURF.fill((35, 35, 55))
        all_sprites.draw(window.DISPLAYSURF)


        pygame.display.update()



if __name__ == '__main__':
    main()
