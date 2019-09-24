__author__ = 'Matt'

import pygame, sys, os
from pygame.locals import *
import numpy as np
import random


# global variables
g_GAMEDIR = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]      # base script path, for relative resource gathering
g_SPRITEDIR = os.path.join(g_GAMEDIR, 'sprites')                                    # sprite directory, relative to base path
g_game_state = 'menu screen'                                                      # the main game state
g_game_stats = {'player1': {'score': 000, 'lives': 3, 'powerup': ''},
              'player2': {'score': 000, 'lives': 3, 'powerup': ''}}                         # tracks game stats
g_COLOURS = {'BLACK': (0, 0, 0), 'GREEN': (0, 255, 0), 'L_BLUE': (130, 220, 255), # some default g_COLOURS
           'RED': (255, 0, 0)}


player_sprites = pygame.sprite.Group()          # All player sprites
player_draw_sprites = pygame.sprite.Group()     # Player sprites to draw
player_update_sprites = pygame.sprite.Group()   # Player sprites to update

asteroid_dict = pygame.sprite.Group()        # All asteroids to draw and update
projectile_sprites = pygame.sprite.Group()      # All projectiles to draw and update
explosion_sprites = pygame.sprite.Group()       # All explosion sprites to draw and update

UI_sprites = pygame.sprite.Group()              # All UI sprites
UI_draw_sprites = pygame.sprite.Group()         # All UI sprites to draw
UI_update_sprites = pygame.sprite.Group()       # All UI sprites to update


class Window(object):

    DISPLAYSURF = ''

    def __init__(self, WINDOW_SIZE=(1280, 1024), CAPTION='your caption here'): # class constructor
        self.WINDOW_SIZE = WINDOW_SIZE
        self.DISPLAYSURF = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
        pygame.display.set_caption(CAPTION)

    def get_center(self):
        return (int(self.WINDOW_SIZE[0] / 2), int(self.WINDOW_SIZE[1] / 2))


class SpaceObject(pygame.sprite.Sprite):

    global g_game_state, g_game_stats, g_SPRITEDIR, g_COLOURS

    def __init__(self, window, spritesize = (20, 20), position_by='center'):
        pygame.sprite.Sprite.__init__(self)         # init the parent class
        #print('SpaceObject init')

        self.window = window                        # main window for querying stuff like screen size
        self.owner = None                           # who owns this object, e.g. player1 owns a projectile
        self.position_by = position_by              # set position by what part of the bbox, default is center
        self.position = pygame.Vector2(0, 0)        # screen space position of the sprite
        self.orientation = 0                        # orientation of the sprite in degrees
        self.motion_vector = pygame.Vector2(0, 0)   # the motion vector of the sprite
        self.wraparound = False                     # enable/disable screen wraparound
        self.scoring_value = 0                      # scoring value of object when destroyed
        self.damage = 100                           # damage this object does to another on collision
        self.health = 100                           # this object health
        self.lives = 1                              # this object number of lives
        self._invulnerable = False                  # is the object invulnerable? - private, not to be directly modified
        self._invulnerability_end = 0               # time when invulnerability ends
        self.do_collision_check = False             # enable/disable collision checks for this sprite
        self.last_collision_check = 0               # time in milliseconds of last collision check
        self.last_collision_owner = None            # stores the owner of the last colliding object

        self.image_original = pygame.Surface(spritesize)    # always clean version of the sprite image, updated from here on self.update
        self.image_original.fill((g_COLOURS['L_BLUE']))       # default square fill in place of an image
        self.image = self.image_original.copy()             # actual image drawn

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

    def on_health_zero(self):  # what to do when sprite health hits zero
        pygame.sprite.Sprite.kill(self)

    def make_invulnerable(self, countdown=3000):  # make object invulnerable for countdown milliseconds
        self._invulnerability_end = pygame.time.get_ticks() + countdown
        self._invulnerable = True
        self.on_invulnerable()

    def on_invulnerable(self):  # what to do when object made invulnerable
        # e.g. change sprite to add a shield effect
        print('{0} is invulnerable '.format(self))

    def on_end_invulnerable(self):  #waht to do when object made vulnerable
        # e.g. change sprite back to remove shield effect
        print('{0} is no longer invulnerable')

    def on_collide(self, colliding_object, callback=True):  # what to do when a collision is detected
        if self._invulnerable:
            pass
        else:
            # get damage value of colliding object & subtract from self health
            self.health -= colliding_object.damage
            # get the owner of the colliding object, e.g projectile, use this for assigning scores
            self.last_collision_owner = colliding_object.owner
        # call on_collide function of the other object, passing this one. Callback flag is to prevent recursion
        if callback:
            colliding_object.on_collide(self, callback=False)

    def collision_check(self, objects=[]):  # checks for collisions against sprites in passed list
        if self.do_collision_check:
            for object in objects:
                if pygame.sprite.collide_circle(self, object):
                    self.on_collide(colliding_object=object)  # call the on_collide method, passing the colliding object
                    break  # run no further collision checks if collide detected

    def set_wraparound(self):
        # wraparound behaviour, false by default. This method can be overwritten to modify this (see Asteroid class)
        return False

    def update_motion_vector(self):
        # modify the motion vector here
        pass

    def update_orientation(self):
        # modify the sprite rotation here
        pass

    def before_update(self):
        # do something before the update
        pass

    def on_end_update(self):
        # do something after the update
        pass

    def update(self):  # the main update method
        self.before_update()

        if self.health > 0:
            if self._invulnerable:  # check invulnerability countdown
                if self._invulnerability_end < pygame.time.get_ticks():
                    self._invulnerability_end = 0  # reset the end time
                    self._invulnerable = False
                    self.on_end_invulnerable()

            self.update_motion_vector()     # optionally change the motion vector
            self.update_orientation()       # optionally change the orientation

            # update sprite rotation
            old_center = self.rect.center  # cache the center of the current sprite rect
            self.image = pygame.transform.rotate(self.image_original, self.orientation)  # recreate image from clean transform of original
            self.rect = self.image.get_rect()  # grab the rect of the new image
            self.rect.center = old_center  # ... and position it in the same center as the previous one
            self.image.set_colorkey(g_COLOURS['BLACK'])  # new image, so need to colour key

            # update sprite position
            self.wraparound = self.set_wraparound()  # check if conditions have been met to enable/disable wraparound

            if self.wraparound:
                # screen position wrap around
                if self.position.x < -self.screenpadding:
                    self.position.x = self.window.WINDOW_SIZE[0] + self.screenpadding
                if self.position.x > self.window.WINDOW_SIZE[0] + self.screenpadding:
                    self.position.x = -self.screenpadding
                if self.position.y < -self.screenpadding:
                    self.position.y = self.window.WINDOW_SIZE[1] + self.screenpadding
                if self.position.y > self.window.WINDOW_SIZE[1] + self.screenpadding:
                    self.position.y = -self.screenpadding

            self.position += self.motion_vector
            if self.position_by == 'center':
                self.rect.center = self.position
            if self.position_by == 'midleft':
                self.rect.midleft = self.position
            if self.position_by == 'midright':
                self.rect.midright = self.position
            if self.position_by == 'midtop':
                self.rect.midtop = self.position
            if self.position_by == 'midbottom':
                self.rect.midbottom = self.position
            if self.position_by == 'topleft':
                self.rect.topleft = self.position
            if self.position_by == 'topright':
                self.rect.topright = self.position
            if self.position_by == 'bottomleft':
                self.rect.bottomleft = self.position
            if self.position_by == 'bottomright':
                self.rect.bottomright = self.position
        else:
            # unless heath has dropped to zero or below
            self.on_health_zero()

        self.on_end_update()    # optionally, do something after the update


class Player(SpaceObject):

    # static properties
    TYPE = 'Player'
    THRUST_V = pygame.Vector2(0,-0.05)  # the polar vector of a thrust impulse
    MAX_ROTATION_STEP = 4               # the max step value (per frame) of a rotation
    MIN_ROTATION_STEP = 0.001           # the min step value (per frame) of a rotation
    INERTIA = 99.5                      # motion vector decay rate (as a percentage) of the movement vector
    ROTATION_DECAY = 97                 # the rotation step decay rate
    DEFAULT_HEALTH = 100

    def __init__(self, window, name='player1'):  # class constructor
        SpaceObject.__init__(self, window)  # init the parent class
        self.name = name        # default name, used to access game stat dict
        self.owner = name       # who owns this sprite, used in collision to track scoring
        self.state = 'playing'  # dead, playing, awaiting respawn, teleporting
        self.sprite_state = 'default'

        self.window = window  # store a link to the window obj so we can query info about it

        # class properties
        self.thrust_vector = pygame.Vector2(0,0)    # thrust vector, added to the motion vector
        self.rotate_step = self.MIN_ROTATION_STEP   # rotation step, changes to give ease-in behaviour
        self.last_rotate_direction = None           # rotate tracker, part of the rotation ease-in code
        self.last_fire = 0                          # time in milliseconds since last fired
        self.firing_interval = 200                  # interval in millisecond between firing
        self.projectile_speed = 3                   # speed of fired projectile
        self.lives = 3                              # number of player lives
        self.do_collision_check = True              # whether to perform the collision check
        self.health = self.DEFAULT_HEALTH           # set heath to default value

        g_game_stats[name]['score'] = 0
        g_game_stats[name]['lives'] = self.lives

        # load our sprites, keep an original as rotation is lossy!
        self.player_sprites = {'default': pygame.image.load(os.path.join(g_SPRITEDIR, 'player.png')),
                               'thrust': pygame.image.load(os.path.join(g_SPRITEDIR, 'player_thrust.png')),
                               'shield': pygame.image.load(os.path.join(g_SPRITEDIR, 'player_shield.png')),
                               'thrust_shield': pygame.image.load(os.path.join(g_SPRITEDIR, 'player_thrust_shield.png'))}
        self.image = self.player_sprites['default'].copy()
        self.ship_original = self.image.copy()

        self.rebuild()  # reset rect, radius and screen wrap padding values to new loaded image

        # initial spawn position
        self.position.xy = window.get_center()[0], window.get_center()[1]
        self.rect.center = self.position

    def on_health_zero(self):
        self.lives -= 1
        if self.lives > 0:
            print('Lost a life, you clumsy oaf')
            self.state = 'health zero'
            g_game_stats[self.name]['lives'] = self.lives
        if self.lives == 0:
            print('He\'s dead, Jim')
            self.state = 'dead'

    def set_wraparound(self):
        return True

    def rotate(self, direction):
        # reset the rotation step to min if the rotation direction has changed
        if not self.last_rotate_direction:
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
        # set sprite state
        if self._invulnerable:
            self.sprite_state = 'thrust_shield'
        else:
            self.sprite_state = 'thrust'

        # rotate polar thrust vector to ship orientation to give our final thrust vector
        self.thrust_vector = self.THRUST_V.rotate(self.orientation*-1)
        self.motion_vector += self.thrust_vector
        # set thrust vector to zero, else it'll keep adding
        self.thrust_vector.xy = 0, 0

    def update_motion_vector(self):
        # decay the main vector
        self.motion_vector.x = (self.motion_vector.x / 100) * self.INERTIA
        self.motion_vector.y = (self.motion_vector.y / 100) * self.INERTIA
        # add the thrust vector to the main motion vector
        self.motion_vector += self.thrust_vector

    def update_orientation(self):
        # update rotation
        # decay the rotation step
        self.rotate_step = (self.rotate_step / 100) * self.ROTATION_DECAY
        self.rotate_step = np.clip(self.rotate_step, self.MIN_ROTATION_STEP, self.MAX_ROTATION_STEP)
        # constrain to 0-360 so we don't have mental orientation values
        if self.orientation > 360:
            self.orientation -= 360
        if self.orientation < 0:
            self.orientation += 360

    def before_update(self):  # set sprites according to self.sprite_state
        self.image_original = self.player_sprites[self.sprite_state]

    def on_end_update(self):
        # do something afer the update
        # set sprite state
        if self._invulnerable:
            self.sprite_state = 'shield'
        else:
            self.sprite_state = 'default'


class Asteroid(SpaceObject):

    # static properties
    TYPE = 'Asteroid'
    MIN_ROTATE_SPEED = 0
    MAX_ROTATE_SPEED = 10
    SPAWN_SCREEN_PAD = -100

    # resource definitions
    asteroid_a = {1:{'image': 'asteroid_01_a.png', 'v_scale': 1, 'score': 1, 'health': 100, 'fragments': 3, 'gravity': 0},
                  2:{'image': 'asteroid_01_b.png', 'v_scale': 2, 'score': 1, 'health': 100, 'fragments': 3, 'gravity': 0},
                  3:{'image': 'asteroid_01_c.png', 'v_scale': 4, 'score': 1, 'health': 100, 'fragments': 0, 'gravity': 0}}

    asteroid_b = {1:{'image': 'asteroid_01_a.png', 'v_scale': 1, 'score': 1, 'health': 100, 'fragments': 3, 'gravity': 0},
                  2:{'image': 'asteroid_01_b.png', 'v_scale': 2, 'score': 1, 'health': 100, 'fragments': 3, 'gravity': 0},
                  3:{'image': 'asteroid_01_c.png', 'v_scale': 4, 'score': 1, 'health': 100, 'fragments': 0, 'gravity': 0}}

    asteroid_c = {1:{'image': 'asteroid_03_a.png', 'v_scale': 1, 'score': 1, 'health': 100, 'fragments': 3, 'gravity': 0},
                  2:{'image': 'asteroid_03_b.png', 'v_scale': 2, 'score': 1, 'health': 100, 'fragments': 3, 'gravity': 0},
                  3:{'image': 'asteroid_03_c.png', 'v_scale': 4, 'score': 1, 'health': 100, 'fragments': 0, 'gravity': 0}}

    asteroid_d = {1:{'image': 'asteroid_04_a.png', 'v_scale': 1, 'score': 10, 'health': 100, 'fragments': 3, 'gravity': 0},
                  2:{'image': 'asteroid_04_b.png', 'v_scale': 2, 'score': 10, 'health': 100, 'fragments': 3, 'gravity': 0},
                  3:{'image': 'asteroid_04_c.png', 'v_scale': 4, 'score': 10, 'health': 100, 'fragments': 0, 'gravity': 0}}

    def __init__(self, window, stage=1, spawn_position=False, asteroid_dict={}):  # class constructor
        SpaceObject.__init__(self, window)  # init the parent class

        self.window = window

        self.stage = stage
        # pick random asteroid
        self.asteroid_dict = asteroid_dict
        if not len(self.asteroid_dict):
            self.asteroid_dict = np.random.choice([self.asteroid_a, self.asteroid_b, self.asteroid_c, self.asteroid_d], 1)[0]

        v_scale = self.asteroid_dict[self.stage]['v_scale']
        self.health = self.asteroid_dict[self.stage]['health']              # number of fragments to split into
        self.min_velocity = 0.05 * v_scale                                  # default values for 120 x 120 sprite
        self.max_velocity = 0.4 * v_scale                                   # default values for 120 x 120 sprite
        self.min_rotation_speed = 0.1 * v_scale                             # default values for 120 x 120 sprite
        self.max_rotation_speed = 0.3 * v_scale                             # default values for 120 x 120 sprite
        self.number_fragments = self.asteroid_dict[self.stage]['fragments'] # number of fragments to split into
        self.scoring_value = self.asteroid_dict[self.stage]['score']        # scoring value on destroyed


        self.image_original = pygame.image.load(os.path.join(g_SPRITEDIR, self.asteroid_dict[self.stage]['image']))

        self.image = self.image_original.copy()

        self.rebuild()  # reset rect, radius and screen wrap padding values to new loaded image


        # SPAWNING
        # build polar vector of x = 0, y = rand min->max
        self.motion_vector = pygame.Vector2(0, random.uniform(self.min_velocity, self.max_velocity))
        # set rotation speed, pick between rand min/max and direction
        self.rotation_speed = random.uniform(self.min_rotation_speed, self.max_rotation_speed) * np.random.choice([1, -1])

        if spawn_position:
            # spawn at given position
            self.position = pygame.Vector2(spawn_position[0], spawn_position[1])
            self.motion_vector = self.motion_vector.rotate(random.randint(0, 360))
        else:
            # pick random side to spawn - top, left, right, bottom
            spawnside = np.random.choice(['top', 'bottom', 'left', 'right'], 1)[0]
            # pick random (range constrained) position and vector rotate to start
            if spawnside == 'top':
                self.position = pygame.Vector2(random.randint(0, window.WINDOW_SIZE[0]), self.SPAWN_SCREEN_PAD)
                self.motion_vector = self.motion_vector.rotate((random.randint(-80, 80)) - 1)
            if spawnside == 'left':
                self.position = pygame.Vector2(self.SPAWN_SCREEN_PAD, random.randint(0, window.WINDOW_SIZE[1]))
                self.motion_vector = self.motion_vector.rotate((random.randint(10, 170)) * -1)
            if spawnside == 'right':
                self.position = pygame.Vector2(window.WINDOW_SIZE[0] - self.SPAWN_SCREEN_PAD,
                                               random.randint(0, window.WINDOW_SIZE[1]))
                self.motion_vector = self.motion_vector.rotate((random.randint(190, 350)) * -1)
            if spawnside == 'bottom':
                self.position = pygame.Vector2(random.randint(0, window.WINDOW_SIZE[0]),
                                               window.WINDOW_SIZE[1] - self.SPAWN_SCREEN_PAD)
                self.motion_vector = self.motion_vector.rotate((random.randint(100, 260)) - 1)

        self.rect.center = self.position

    def update_orientation(self):
        self.orientation += self.rotation_speed

    def set_wraparound(self):  # overrides inherited method to allow spawning off screen, with wraparound set to true once visible
        if self.position.x > 0 and self.position.x < self.window.WINDOW_SIZE[0]:
            if self.position.y > 0 and self.position.y < self.window.WINDOW_SIZE[1]:
                self.wraparound = True
        return self.wraparound
    
    def on_health_zero(self):
        #print('{0} on heath zero with last collision owner: {1}'.format(self, self.last_collision_owner))
        if self.last_collision_owner:  # if the last collision has an owner, e.g asteroid hit by projectile, increment scores
            g_game_stats[self.last_collision_owner]['score'] = g_game_stats[self.last_collision_owner]['score'] + self.scoring_value
            #print(g_game_stats)
            #  tidy up the above, maybe have a game stat manager class with a simpler interface
        if not self.stage == 3:
            for i in range(self.number_fragments):
                ast = Asteroid(self.window, stage=self.stage+1, spawn_position=self.rect.center, asteroid_dict=self.asteroid_dict)
                asteroid_dict.add(ast)
        pygame.sprite.Sprite.kill(self)


class Projectile(SpaceObject):

    # static properties
    TYPE = 'Projectile'

    def __init__(self, window, position, ship_vector, ship_orientation, speed, spawntime, owner):  # class constructor
        SpaceObject.__init__(self, window, spritesize=(2, 2))  # init the parent class

        self.position += position
        self.speed = speed
        self.orientation = ship_orientation
        self.motion_vector.xy = 0, self.speed * -1
        self.motion_vector = self.motion_vector.rotate(self.orientation * -1)
        self.motion_vector += ship_vector
        self.owner = owner

        self.do_collision_check = True
        self.spawntime = spawntime
        self.health = 1
        self.damage = 100
        self.lifespan = 1500  # milliseconds
        self.window = window

        self.rebuild()

    def set_wraparound(self):
        return True


class AnimatingObject(SpaceObject):

    def __init__(self, window, subfolder='explosion_001', fps=12, loop=False, max_loops=-1, position=(0, 0)):  # class constructor
        SpaceObject.__init__(self, window)  # init the parent class

        self.position.xy = position[0], position[1]
        # construct the sprite path - should be subfolder which contains only anim frames for this sprite
        sprite_dir = os.path.realpath(os.path.join(g_SPRITEDIR, subfolder))
        # return all images in this dir (sequence)
        image_sequence = [f for f in os.listdir(sprite_dir) if os.path.isfile(os.path.join(sprite_dir, f))]
        self.images = []                    # list of pygame image objects
        self.image_index = 1                # tracks which image in list to use
        for image in image_sequence:
            self.images.append(pygame.image.load(os.path.realpath(os.path.join(sprite_dir, image))))
        self.image_original = self.images[0]         # set initial sprite image to first in sequence
        self.rebuild()                      # rebuild the image rect
        self.tick_increment = 1000 / fps    # set time increment on which to change to next image in sequence
        self.next_image_tick = pygame.time.get_ticks() + self.tick_increment  # set the tick time to set next image in seq
        self.loop = loop                    # should we loop
        self.max_loops = max_loops          # max loops, -1 if infinite
        self.loop_counter = 0               # loop count tracker


    def before_update(self):
        this_time = pygame.time.get_ticks()
        if this_time > self.next_image_tick:  # check if time to change image
            self.image_original = self.images[self.image_index]      # ...if so, change the image
            self.image_index += 1                           # increment the image index
            if self.image_index < len(self.images):         # if image index is out of range, either loop or exit
                if self.loop:
                    self.image_index = 0                    # ...looping, reset index
                    self.loop_counter += 1                  # increment the loop counter
                    if not self.max_loops == -1:            # check not over max loops
                        if self.loop_counter >= self.max_loops:     # ...if so...
                            self.loop = False                       # set loop to false
            else:
                self.on_health_zero()
            self.next_image_tick = this_time + self.tick_increment


class TextObject(SpaceObject):

    def __init__(self, window, font='freesansbold.ttf', size=32, colour=g_COLOURS['GREEN'], text='Hello World!',
                 position_by='center', position=(0, 0), game_stat_keys=['', '']):
        SpaceObject.__init__(self, window, position_by=position_by)
        self.position.xy = position[0], position[1]
        self.fontObj = pygame.font.Font(font, size)  # create a font object
        self.colour = colour
        self.image_original = self.fontObj.render(text, True, self.colour, g_COLOURS['BLACK']) # create surface obj with text drawn on it
        self.image = self.image_original.copy()
        self.image.set_colorkey((g_COLOURS['BLACK']))
        self.rebuild()

        if self.position_by == 'center':
            self.rect.center = self.position
        if self.position_by == 'midleft':
            self.rect.midleft = self.position
        if self.position_by == 'midright':
            self.rect.midright = self.position
        if self.position_by == 'midtop':
            self.rect.midtop = self.position
        if self.position_by == 'midbottom':
            self.rect.midbottom = self.position
        if self.position_by == 'topleft':
            self.rect.topleft = self.position
        if self.position_by == 'topright':
            self.rect.topright = self.position
        if self.position_by == 'bottomleft':
            self.rect.bottomleft = self.position
        if self.position_by == 'bottomright':
            self.rect.bottomright = self.position

        self.player_key = None
        self.stat_key = None
        if game_stat_keys[0] in g_game_stats:
            if game_stat_keys[1] in g_game_stats[game_stat_keys[0]]:
                self.player_key = game_stat_keys[0]
                self.stat_key = game_stat_keys[1]
        #print(self.player_key, self.stat_key)


    def update(self):
        if not self.player_key == None and not self.stat_key == None:
            text = g_game_stats[self.player_key][self.stat_key]
            self.image = self.fontObj.render(str(text), True, self.colour, g_COLOURS['BLACK'])
            self.image.set_colorkey((g_COLOURS['BLACK']))





def main(): # main game code

    pygame.init()
    # some constants...
    FPS = 120                   # set frames per second
    COLLISION_TICK = 16         # tick interval in milliseconds for collision detection
    next_collision_update = 0   # time for next collision update
    UI_TICK = 250               # tick interval in milliseconds for UI update
    next_UI_update = 0          # time for next UI update
    RESPAWN_DELAY = 3000        # re-spawn delay time in milliseconds
    clock = pygame.time.Clock() # clock to allow millisecond-based (i.e frame-rate independent) timing
    multiplayer = False         # single or multi-layer

    # create the window
    window = Window(WINDOW_SIZE=(1600, 1024), CAPTION='player movement test')  # instance a window for the game

    # player1 keyboard mappings
    INPUT_ROTATE_CCW = 'left_arrow'
    INPUT_ROTATE_CW = 'right_arrow'
    INPUT_THRUST = 'up_arrow'
    INPUT_FIRE = 'space'

    # spawn the in game UI
    UI_objects = []
    UI_objects.append(TextObject(window=window, size=28, colour=g_COLOURS['RED'], text='Player 1', position_by='midleft',
                                 position=(20, 20)))
    UI_objects.append(TextObject(window=window, size=28, colour=g_COLOURS['RED'], text='0000', position_by='midleft',
                                 position=(20, 55), game_stat_keys=['player1', 'score']))
    UI_objects.append(TextObject(window=window, size=28, colour=g_COLOURS['RED'], text='3', position_by='midleft',
                                 position=(20, 90), game_stat_keys=['player1', 'lives']))
    for UI_object in UI_objects:
        UI_draw_sprites.add(UI_object)
        UI_update_sprites.add(UI_object)

    # spawn the player
    player1 = Player(window=window, name='player1')
    player_sprites.add(player1)
    player_update_sprites.add(player1)
    player_draw_sprites.add(player1)
    player_awaiting_respawn = {}   # dict of players awaiting re-spawn, contains player object and time

    # spawn some asteroids!
    asteroid_spawn_interval = 10000  # in milliseconds
    num_initial_asteroids = 4

    asteroid_list = []
    for i in range(num_initial_asteroids):
        ast = Asteroid(window)
        asteroid_dict.add(ast)
    last_asteroid_spawntime = 0
    print('asteroid spawned, next one in {0} milliseconds'.format(asteroid_spawn_interval))

    while True:  # main game loop
        clock.tick(FPS)
        timenow = pygame.time.get_ticks()


        # asteroid spawn manager
        if timenow > last_asteroid_spawntime + asteroid_spawn_interval:
            # spawn another asteroid
            asteroid_dict.add(Asteroid(window))
            if asteroid_spawn_interval > 4000:
                asteroid_spawn_interval -= 100
            print('asteroid spawned, next one in {0} milliseconds'.format(asteroid_spawn_interval))
            last_asteroid_spawntime = timenow


        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        keystate = pygame.key.get_pressed()
        # player1 input handling
        if player1.state == 'playing':
            if keystate[pygame.K_a]:
                player1.rotate(direction='ccw')
            if keystate[pygame.K_d]:
                player1.rotate(direction='cw')
            if keystate[pygame.K_w]:
                player1.thrust()
            if keystate[pygame.K_SPACE]:
                if (timenow - player1.last_fire) > player1.firing_interval:
                    # instance the projectile class here
                    projectile = Projectile(window=window, position=player1.position, ship_vector=player1.motion_vector,
                                            ship_orientation=player1.orientation, speed=player1.projectile_speed,
                                            spawntime=timenow, owner=player1.name)
                    projectile_sprites.add(projectile)
                    player1.last_fire = timenow

        # check for end-of-life projectiles and kill
        for projectile in projectile_sprites:
            if (projectile.spawntime + projectile.lifespan) < timenow:
                pygame.sprite.Sprite.kill(projectile)


        # Collision checks
        if timenow >= next_collision_update:
            for projectile in projectile_sprites:  #
                projectile.collision_check(asteroid_dict)
                projectile.last_collision_check = timenow
            for player in player_draw_sprites:
                player.collision_check(asteroid_dict)
                player.last_collision_check = timenow
            next_collision_update = timenow + COLLISION_TICK


        # Check player states and manage group membership # dead, playing, health zero, awaiting re-spawn, teleporting
        for player in player_sprites:
            if player.state == 'dead':
                #spawn an explosion at player position
                explosion = AnimatingObject(window=window, position=player.position)
                explosion_sprites.add(explosion)
                pygame.sprite.Sprite.kill(player)
            if player.state == 'health zero':
                #spawn an explosion at player position
                explosion = AnimatingObject(window=window, position=player.position)
                explosion_sprites.add(explosion)
                # remove from draw and update group
                player_draw_sprites.remove(player)
                player_update_sprites.remove(player)
                # add to awaiting re-spawn dict with time now to track awaiting respawn time
                player_awaiting_respawn[player] = timenow
                # set state to awaiting re-spawn
                player.state = 'awaiting re-spawn'
                # set health to default
                player.health = player.DEFAULT_HEALTH


        # re-spawn manager
        keys = []
        for player, death_time in player_awaiting_respawn.items():
            if timenow >= death_time + RESPAWN_DELAY:
                print('Re-spawing {0}'.format(player))
                # reset player position, orientation and motion vector
                player.position.xy = window.get_center()[0], window.get_center()[1]
                player.motion_vector.xy = 0, 0
                player.orientation = 0
                player.make_invulnerable(countdown=3000)  # make the player invulnerable for countdown milliseconds
                # add player back into the update and draw groups
                player_draw_sprites.add(player)
                player_update_sprites.add(player)
                player.state = 'playing'
                keys.append(player)
        for key in keys:  # can't modify a dict length while iterating over it, so do outside of the iterator
            del player_awaiting_respawn[key]

        # Update
        player_update_sprites.update()
        asteroid_dict.update()
        projectile_sprites.update()
        explosion_sprites.update()
        if timenow >= next_UI_update:
            UI_update_sprites.update()
            next_UI_update = timenow + UI_TICK

        # Draw
        window.DISPLAYSURF.fill((35, 35, 55))
        projectile_sprites.draw(window.DISPLAYSURF)
        asteroid_dict.draw(window.DISPLAYSURF)
        player_draw_sprites.draw(window.DISPLAYSURF)
        explosion_sprites.draw(window.DISPLAYSURF)
        UI_draw_sprites.draw(window.DISPLAYSURF)


        # update display
        pygame.display.update()



if __name__ == '__main__':
    main()



'''



To Do:



fire rate decay
teleporting
add starting health to asteroid dict, plus hit but not die effect (flash)
...for massive asteroids, add extra stages
powerup drops from asteroids - lives, damage, fire rate, teleports
add probability spread to asteroid types

add flying saucer that shoots at you
multiplayer
multiplayer drops that affect the opponent - speed, instability?


'''




