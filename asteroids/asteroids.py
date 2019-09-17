__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *
import numpy as np
import random
import math




#nparray = np.array([0,0])
#nparray[1] = 6
#for m in dir(nparray):
#    print(m)

# global variables
GAMEDIR = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
SPRITEDIR = os.path.join(GAMEDIR, 'sprites')
GameState = 'menu screen'
COLOURS = {'BLACK': (0, 0, 0), 'GREEN': (0, 255, 0)}

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
    global GameState, SPRITEDIR, COLOURS

    # static properties
    THRUST_V = pygame.Vector2(0,-0.05)  # the polar vector of a thrust impulse
    MAX_ROTATION_STEP = 4  # the max step value (per frame) of a rotation
    MIN_ROTATION_STEP = 0.001  # the min step value (per frame) of a rotation
    INERTIA = 99.5  # decay rate (as a percentage) of the movement vector
    ROTATION_DECAY = 97  # the rotation step decay rate

    # class properties
    type = 'Player'
    state = 'Inactive'
    player_name = ''
    score = 0
    lives = 3
    firespeed = 500  # interval in milliseconds
    position = pygame.Vector2(0,0)
    orientation = 0
    motion_vector = pygame.Vector2(0,0)
    thrust_vector = pygame.Vector2(0,0)
    rotate_step = MIN_ROTATION_STEP
    last_rotate_direction = None



    def __init__(self, window):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class
        self.window = window  # store a link to the window obj so we can query info about it
        self.ship_original = pygame.image.load(os.path.join(SPRITEDIR, 'player.png'))#.convert()
        self.ship_original = pygame.transform.smoothscale(self.ship_original, (26, 38))
        self.shipthrust_original = pygame.image.load(os.path.join(SPRITEDIR, 'player_thrust.png'))#.convert()
        self.shipthrust_original = pygame.transform.smoothscale(self.shipthrust_original, (26, 38))
        self.image_original = self.ship_original.copy()
        self.image = self.image_original.copy()  # this one will be the transformed result of ...orig
        self.image.set_colorkey((COLOURS['BLACK']))
        self.screenpadding = (self.image_original.get_rect().size[0] / 2)
        self.rect = self.image.get_rect()
        self.position.xy = window.get_center()[0], window.get_center()[1]
        self.rect.center = self.position
        self.last_update = 0

    def explode(self):  # triggered if collision between player and asteroid
        self.state = 'Exploding'
        self.draw = False  # set flag so ship isn't drawn until re-spawned
        self.lives -= 1
        if self.lives == 0:
            GameState = 'game over'

    def fire(self):
        timenow = pygame.time.get_ticks()
        lastfire = 0
        print(timenow, lastfire)
        if (timenow - lastfire) > self.firespeed:
            print('fire')
        lastfire = timenow


    def rotate(self, direction):
        '''
        Generates the amount to rotate for the frame. The rotation step amount eases in.
        '''
        # check when last rotated by milliseconds - this locks rotation rate to clock rather than tick
        timenow = pygame.time.get_ticks()
        if timenow - self.last_update > 16.6666:
            if not self.last_rotate_direction:  #
                self.last_rotate_direction = direction
            if not direction == self.last_rotate_direction:
                self.rotate_step = self.MIN_ROTATION_STEP
                self.last_rotate_direction = direction
            this_rotate = self.rotate_step
            if direction == 'cw':
                this_rotate = self.rotate_step *-1
            self.orientation += this_rotate # add this rotate into ship orientation
            self.rotate_step += 0.5  # increment the rotate step, so rate of rotation accelerates (up to max)
            self.rotate_step = np.clip(self.rotate_step, 0, self.MAX_ROTATION_STEP)  # clamp to min/max

    def thrust(self):
        self.image_original = self.shipthrust_original.copy()
        # rotate polar thrust vector to ship orientation to give our final thrust vector
        self.thrust_vector = self.THRUST_V.rotate(self.orientation*-1)
        self.motion_vector += self.thrust_vector
        # set thrust vector to zero, else it'll keep adding
        self.thrust_vector.xy = 0, 0

    def update(self):

    # update rotation
        # decay the rotation step
        self.rotate_step = (self.rotate_step / 100) * self.ROTATION_DECAY
        self.rotate_step = np.clip(self.rotate_step, self.MIN_ROTATION_STEP, self.MAX_ROTATION_STEP)
        # constrain to 0-360 so we don't have mental orientation values
        if self.orientation > 360:
            self.orientation -= 360
        if self.orientation < 0:
            self.orientation += 360
        old_center = self.rect.center  # cache the center of the current sprite rect
        self.image = pygame.transform.rotate(self.image_original, self.orientation)  # recreate image from clean transform of original
        self.rect = self.image.get_rect()  # grab the rect of the new image
        self.rect.center = old_center  # ... and position it in the same center as the previous one
        self.image.set_colorkey(COLOURS['BLACK'])  # new image, so need to colour key


    # update position

        # decay the main vector
        self.motion_vector.x = (self.motion_vector.x / 100) * self.INERTIA
        self.motion_vector.y = (self.motion_vector.y / 100) * self.INERTIA
        # add the thrust vector to the main motion vector
        self.motion_vector += self.thrust_vector
        # update the position with our new vector
        self.position += self.motion_vector
        # screen position wrap around
        if self.position.x < -self.screenpadding:
            self.position.x = self.window.WINDOWSIZE[0] + self.screenpadding
        if self.position.x > self.window.WINDOWSIZE[0] + self.screenpadding:
            self.position.x = -self.screenpadding
        if self.position.y < -self.screenpadding:
            self.position.y = self.window.WINDOWSIZE[1] + self.screenpadding
        if self.position.y > self.window.WINDOWSIZE[1] + self.screenpadding:
            self.position.y = -self.screenpadding
        # finally, update the rect position by assigning the vect to rect.center
        self.rect.center = self.position

        #self.last_update = timenow
        self.image_original = self.ship_original.copy()



class Asteroid(pygame.sprite.Sprite):

    # global variables
    global GameState, SPRITEDIR, COLOURS

    # static properties
    TYPE = 'Asteroid'
    MIN_VECTOR = 0.1
    MAX_VECTOR = 0.75
    MIN_ROTATE_SPEED = 0
    MAX_ROTATE_SPEED = 10
    SPAWN_SCREEN_PAD = -250

    # resource definitions
    asteroid_sprites_a = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}
    asteroid_sprites_b = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}
    asteroid_sprites_c = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}
    asteroid_sprites_d = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}


    def __init__(self, window):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class

        self.asteroid_sprites = {}
        self.position = pygame.Vector2()
        self.motion_vector = pygame.Vector2()
        self.orientation = 0
        self.rotation_speed = 1
        self.stage = 1
        self.health = 100

        self.window = window
        # pick random sprite set
        self.asteroid_sprites = np.random.choice([self.asteroid_sprites_a, self.asteroid_sprites_b,
                                                  self.asteroid_sprites_c, self.asteroid_sprites_d], 1)[0]
        self.image_original = pygame.image.load(os.path.join(SPRITEDIR, self.asteroid_sprites[self.stage]))
        self.image_original = pygame.transform.smoothscale(self.image_original, (80, 80))
        self.image = self.image_original.copy()
        self.image.set_colorkey((COLOURS['BLACK']))
        self.rect = self.image.get_rect()
        self.wraparound = False  # initially disable wraparound so we can spawn off screen
        self.screenpadding = (self.image_original.get_rect().size[0] / 2) #  set wrap screen padding to half sprite size


        # pick random side to spawn - top, left, right, bottom
        spawnside = np.random.choice(['top', 'bottom', 'left', 'right'], 1)[0]

        # build polar vector of x = 0, y = rand min->max
        self.motion_vector = pygame.Vector2(0, random.uniform(self.MIN_VECTOR, self.MAX_VECTOR))

        # pick random (range constrained) position and vector rotate to start
        if spawnside == 'top':
            self.position = pygame.Vector2(random.randint(0, window.WINDOWSIZE[0]), self.SPAWN_SCREEN_PAD)
            self.motion_vector = self.motion_vector.rotate((random.randint(-80, 80))-1)
        if spawnside == 'left':
            self.position = pygame.Vector2(self.SPAWN_SCREEN_PAD, random.randint(0, window.WINDOWSIZE[1]))
            self.motion_vector = self.motion_vector.rotate((random.randint(10, 170))*-1)
        if spawnside == 'right':
            self.position = pygame.Vector2(window.WINDOWSIZE[0] - self.SPAWN_SCREEN_PAD, random.randint(0, window.WINDOWSIZE[1]))
            self.motion_vector = self.motion_vector.rotate((random.randint(190, 350))*-1)
        if spawnside == 'bottom':
            self.position = pygame.Vector2(random.randint(0, window.WINDOWSIZE[0]), window.WINDOWSIZE[1] - self.SPAWN_SCREEN_PAD)
            self.motion_vector = self.motion_vector.rotate((random.randint(100, 260))-1)

        self.rect.center = self.position


    def update(self):
        
        if not self.wraparound:  # check to see if we should enable wraparound positioning, this is disabled at first
            if self.position.x > 0 and self.position.x < self.window.WINDOWSIZE[0]:
                if self.position.y > 0 and self.position.y < self.window.WINDOWSIZE[1]:
                    self.wraparound = True
        
        # screen position wrap around
        if self.position.x < -self.screenpadding:
            self.position.x = self.window.WINDOWSIZE[0] + self.screenpadding
        if self.position.x > self.window.WINDOWSIZE[0] + self.screenpadding:
            self.position.x = -self.screenpadding
        if self.position.y < -self.screenpadding:
            self.position.y = self.window.WINDOWSIZE[1] + self.screenpadding
        if self.position.y > self.window.WINDOWSIZE[1] + self.screenpadding:
            self.position.y = -self.screenpadding
        
        self.position += self.motion_vector
        self.rect.center = self.position

        

class Projectile(pygame.sprite.Sprite):
    # global variables
    global GameState, SPRITEDIR, COLOURS

    # static properties
    TYPE = 'Projectile'



    def __init__(self, window, position, vector):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class

        self.position = pygame.Vector2()
        self.motion_vector = pygame.Vector2()
        self.orientation = 0
        self.life = 300  # milliseconds

        self.window = window

        self.image_original = pygame.Surface((2, 10))
        self.image_original.fill()

        self.image = self.image_original.copy()
        self.image.set_colorkey((COLOURS['GREEN']))
        self.rect = self.image.get_rect()
        self.wraparound = False  # initially disable wraparound so we can spawn off screen
        self.screenpadding = (self.image_original.get_rect().size[1] / 2)  # set wrap screen padding to half sprite size





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





def main(): # main game code

    pygame.init()
    # some constants...
    FPS = 120 # set frames per second

    # keyboard mappings
    INPUT_ROTATE_CCW = 'left_arrow'
    INPUT_ROTATE_CW = 'right_arrow'
    INPUT_THRUST = 'up_arrow'
    INPUT_FIRE = 'space'

    clock = pygame.time.Clock()
    window = Window(CAPTION='player movement test')  # instance a window for the game
    player = Player(window)
    all_sprites = pygame.sprite.Group()  # all sprites are no24w in this group, makes update and draw easy!
    all_sprites.add(player)

    asteroid_spawn_interval = 10000  # in milliseconds
    num_initial_asteroids = 8
    asteroid_sprites = pygame.sprite.Group()
    asteroid_list = []

    for i in range(num_initial_asteroids):
        print('spawning asteroid')
        ast = Asteroid(window)
        asteroid_list.append(ast)
        asteroid_sprites.add(ast)



    while True: # main game loop
        clock.tick(FPS)

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            player.rotate(direction='ccw')
        if keystate[pygame.K_RIGHT]:
            player.rotate(direction='cw')
        if keystate[pygame.K_UP]:
            player.thrust()

        if keystate[pygame.K_SPACE]:
            player.fire()

        # Event handling
        for event in pygame.event.get():

            # collision event check and handling
            # if player/asteroid collide detected
                # player.Explode()
                # spawn an explosion

            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        # Update
        all_sprites.update()
        asteroid_sprites.update()


        # Draw
        window.DISPLAYSURF.fill((35, 35, 55))
        all_sprites.draw(window.DISPLAYSURF)
        asteroid_sprites.draw(window.DISPLAYSURF)


        pygame.display.update()



if __name__ == '__main__':
    main()



