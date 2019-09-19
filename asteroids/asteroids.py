__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *
import numpy as np
import random






# global variables
GAMEDIR = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
SPRITEDIR = os.path.join(GAMEDIR, 'sprites')
GameState = 'menu screen'
COLOURS = {'BLACK': (0, 0, 0), 'GREEN': (0, 255, 0), 'L_BLUE': (130, 220, 255)}
player_sprites = pygame.sprite.Group()
asteroid_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()


class Window():

    DISPLAYSURF = ''
    WINDOWSIZE=(1200, 900)
    CAPTION = 'your caption here'

    def __init__(self, WINDOWSIZE=WINDOWSIZE, CAPTION=CAPTION): # class constructor
        self.DISPLAYSURF = pygame.display.set_mode(WINDOWSIZE, 0, 32)
        pygame.display.set_caption(CAPTION)

    def get_center(self):
        return (int(self.WINDOWSIZE[0] / 2), int(self.WINDOWSIZE[1] / 2))



class SpaceObject(pygame.sprite.Sprite):

    global GameState, SPRITEDIR, COLOURS

    def __init__(self, window, spritesize = (20, 20)):
        pygame.sprite.Sprite.__init__(self)         # init the parent class
        #print('SpaceObject init')

        self.window = window                        # main window for querying stuff like screen size

        self.position = pygame.Vector2(0, 0)        # screen space position of the sprite
        self.orientation = 0                        # orientation of the sprite in degrees
        self.motion_vector = pygame.Vector2(0, 0)   # the motion vector of the sprite
        self.wraparound = False                     # enable/disable screen wraparound
        self.damage = 100                           # damage this object does to another on collision
        self.health = 100                           # this object health
        self.lives = 1                              # this object number of lives

        self.do_collision_check = False             # enable/disable collision checks for this sprite
        self.last_collision_check = 0               # time in milliseconds of last collision check

        self.image_original = pygame.Surface(spritesize)
        self.image_original.fill((COLOURS['L_BLUE']))
        self.image = self.image_original.copy()

        self.rebuild() # reset rect, radius and screen wrap padding values to new loaded image


    def rebuild(self):  # rebuilds sprite details - rect, radius and screen wrap padding
        self.rect = self.image.get_rect()
        self.screenpadding = (self.image.get_rect().size[1] / 2)  # set wrap screen padding to half sprite size
        # store radius for collision checks
        rectsize = self.image.get_rect().size
        if rectsize[0] > rectsize[1]:
            self.radius = rectsize[0] / 2
        else:
            self.radius = rectsize[1] / 2


    def on_health_zero(self):
        pygame.sprite.Sprite.kill(self)



    def on_collide(self, colliding_object, callback=True):
        # what to do when a collision is detected
        # get damage value of colliding object & subtract from self health
        self.health -= colliding_object.damage
        # call on_collide function of the other object, passing this one
        if callback:
            colliding_object.on_collide(self, callback=False)


    def collision_check(self, objects=[]):
        # checks for collisions against sprites in passed list
        for object in objects:
            if pygame.sprite.collide_circle(self, object):
                #print('collision event: {0} {1}'.format(self, object))
                self.on_collide(colliding_object=object)
                break  # run no further collision checks if collide detected




    def set_wraparound(self):
        # wraparound behaviour, false by default. This method can be overwritten to modify this (see Asteroid class)
        return False

    def update(self):
        if self.health > 0:
            # update position of sprite and rect for this frame
            self.wraparound = self.set_wraparound()  # check if conditions have been met to enable/disable wraparound

            if self.wraparound:
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
        else:
            # unless heath has dropped to zero or below
            print('{0} health reached zero'.format(self))
            self.on_health_zero()



class Player(pygame.sprite.Sprite):

    # global variables
    global GameState, SPRITEDIR, COLOURS

    # static properties
    TYPE = 'Player'
    THRUST_V = pygame.Vector2(0,-0.05)  # the polar vector of a thrust impulse
    MAX_ROTATION_STEP = 4  # the max step value (per frame) of a rotation
    MIN_ROTATION_STEP = 0.001  # the min step value (per frame) of a rotation
    INERTIA = 99.5  # decay rate (as a percentage) of the movement vector
    ROTATION_DECAY = 97  # the rotation step decay rate


    def __init__(self, window):  # class constructor
        pygame.sprite.Sprite.__init__(self)  # init the parent class

        # class properties
        self.player_name = ''
        self.score = 0
        self.lives = 3
        self.position = pygame.Vector2(0,0)
        self.orientation = 0
        self.motion_vector = pygame.Vector2(0,0)
        self.thrust_vector = pygame.Vector2(0,0)
        self.rotate_step = self.MIN_ROTATION_STEP
        self.last_rotate_direction = None
        self.last_fire = 0 # time in milliseconds since last fired
        self.fire_speed = 100 # interval in millisecond between firing
        self.projectile_speed = 3  # speed of fired projectile

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


    def rotate(self, direction):
        '''
        Generates the amount to rotate for the frame. The rotation step amount eases in.
        '''
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


class Asteroid(SpaceObject):

    # static properties
    TYPE = 'Asteroid'
    MIN_VECTOR = 0.1
    MAX_VECTOR = 0.75
    MIN_ROTATE_SPEED = 0
    MAX_ROTATE_SPEED = 10
    SPAWN_SCREEN_PAD = -100

    # resource definitions
    asteroid_sprites_a = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}
    asteroid_sprites_b = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}
    asteroid_sprites_c = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}
    asteroid_sprites_d = {1: 'asteroid_01_a.png', 2: 'asteroid_02_a.png', 3: 'asteroid_03_a.png'}

    def __init__(self, window):  # class constructor
        SpaceObject.__init__(self, window)  # init the parent class

        self.window = window

        self.rotation_speed = 1
        self.stage = 1
        self.health = 100
        self.do_collision_check = False


        # pick random sprite set
        self.asteroid_sprites = {}
        self.asteroid_sprites = np.random.choice([self.asteroid_sprites_a, self.asteroid_sprites_b,
                                                  self.asteroid_sprites_c, self.asteroid_sprites_d], 1)[0]
        self.image_original = pygame.image.load(os.path.join(SPRITEDIR, self.asteroid_sprites[self.stage]))
        self.image_original = pygame.transform.smoothscale(self.image_original, (80, 80))
        self.image = self.image_original.copy()
        self.image.set_colorkey((COLOURS['BLACK']))

        self.rebuild()  # reset rect, radius and screen wrap padding values to new loaded image


        # SPAWNING

        # pick random side to spawn - top, left, right, bottom
        spawnside = np.random.choice(['top', 'bottom', 'left', 'right'], 1)[0]

        # build polar vector of x = 0, y = rand min->max
        self.motion_vector = pygame.Vector2(0, random.uniform(self.MIN_VECTOR, self.MAX_VECTOR))

        # pick random (range constrained) position and vector rotate to start
        if spawnside == 'top':
            self.position = pygame.Vector2(random.randint(0, window.WINDOWSIZE[0]), self.SPAWN_SCREEN_PAD)
            self.motion_vector = self.motion_vector.rotate((random.randint(-80, 80)) - 1)
        if spawnside == 'left':
            self.position = pygame.Vector2(self.SPAWN_SCREEN_PAD, random.randint(0, window.WINDOWSIZE[1]))
            self.motion_vector = self.motion_vector.rotate((random.randint(10, 170)) * -1)
        if spawnside == 'right':
            self.position = pygame.Vector2(window.WINDOWSIZE[0] - self.SPAWN_SCREEN_PAD,
                                           random.randint(0, window.WINDOWSIZE[1]))
            self.motion_vector = self.motion_vector.rotate((random.randint(190, 350)) * -1)
        if spawnside == 'bottom':
            self.position = pygame.Vector2(random.randint(0, window.WINDOWSIZE[0]),
                                           window.WINDOWSIZE[1] - self.SPAWN_SCREEN_PAD)
            self.motion_vector = self.motion_vector.rotate((random.randint(100, 260)) - 1)

        self.rect.center = self.position



    def set_wraparound(self):  # overrides inherited method to allow spawning off screen, with wraparound set to true once visible
        if self.position.x > 0 and self.position.x < self.window.WINDOWSIZE[0]:
            if self.position.y > 0 and self.position.y < self.window.WINDOWSIZE[1]:
                self.wraparound = True
        return self.wraparound


class Projectile(SpaceObject):

    # static properties
    TYPE = 'Projectile'

    def __init__(self, window, position, ship_vector, ship_orientation, speed, spawntime):  # class constructor
        SpaceObject.__init__(self, window, spritesize=(2, 2))  # init the parent class

        self.position += position
        self.speed = speed
        self.orientation = ship_orientation
        self.motion_vector.xy = 0, self.speed * -1
        self.motion_vector = self.motion_vector.rotate(self.orientation * -1)
        self.motion_vector += ship_vector

        self.do_collision_check = True
        self.spawntime = spawntime
        self.health = 1
        self.damage = 100
        self.lifespan = 2000  # milliseconds
        # print('spawned projectile at {0} with vector {1}'.format(self.position, self.motion_vector))
        self.window = window

        self.rebuild()
        #self.rect = self.image.get_rect()
        #self.screenpadding = (self.image_original.get_rect().size[1] / 2)  # set wrap screen padding to half sprite size

    def set_wraparound(self):
        return True



class Explosion(SpaceObject):

    # resources

    def __init__(self, window):  # class constructor
        SpaceObject.__init__(self, window)  # init the parent class





def main(): # main game code

    pygame.init()
    # some constants...
    FPS = 120               # set frames per second
    COLLISION_TICK = 16     # tick interval in milliseconds for collision detection

    clock = pygame.time.Clock()
    # create the window
    window = Window(CAPTION='player movement test')  # instance a window for the game

    # keyboard mappings
    INPUT_ROTATE_CCW = 'left_arrow'
    INPUT_ROTATE_CW = 'right_arrow'
    INPUT_THRUST = 'up_arrow'
    INPUT_FIRE = 'space'


    # spawn the player
    #player_sprites = pygame.sprite.Group()
    player = Player(window)
    player_sprites.add(player)

    # spawn some asteroids!
    #asteroid_sprites = pygame.sprite.Group()
    asteroid_spawn_interval = 10000  # in milliseconds
    num_initial_asteroids = 8

    asteroid_list = []
    for i in range(num_initial_asteroids):
        #print('spawning asteroid')
        ast = Asteroid(window)
        asteroid_sprites.add(ast)

    # projectile trackers
    #projectile_sprites = pygame.sprite.Group()


    while True: # main game loop
        clock.tick(FPS)
        timenow = pygame.time.get_ticks()


        # check for end-of-life projectiles and kill
        for projectile in projectile_sprites:
            if (projectile.spawntime + projectile.lifespan) < timenow:
                pygame.sprite.Sprite.kill(projectile)


        # input handling

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            player.rotate(direction='ccw')
        if keystate[pygame.K_d]:
            player.rotate(direction='cw')
        if keystate[pygame.K_w]:
            player.thrust()
        if keystate[pygame.K_SPACE]:
            if (timenow - player.last_fire) > player.fire_speed:
                # instance the projectile class here

                projectile = Projectile(window=window, position=player.position, ship_vector=player.motion_vector,
                                        ship_orientation=player.orientation, speed=player.projectile_speed, spawntime=timenow)
                projectile_sprites.add(projectile)
                player.last_fire = timenow



        # Event handling

        for event in pygame.event.get():

            # collision event check and handling
            # if player/asteroid collide detected
                # player.Explode()
                # spawn an explosion

            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        # Collision checks
        for projectile in projectile_sprites:#
            if (timenow - projectile.last_collision_check) > COLLISION_TICK:
                projectile.collision_check(asteroid_sprites)
                projectile.last_collision_check = timenow


        # Update
        player_sprites.update()
        asteroid_sprites.update()
        projectile_sprites.update()


        # Draw
        window.DISPLAYSURF.fill((35, 35, 55))
        projectile_sprites.draw(window.DISPLAYSURF)
        player_sprites.draw(window.DISPLAYSURF)
        asteroid_sprites.draw(window.DISPLAYSURF)


        pygame.display.update()



if __name__ == '__main__':
    main()








