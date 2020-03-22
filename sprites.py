# sprite classes for game
# i used some ideas from CodePylet https://www.youtube.com/watch?v=osDofIdja6s&t=1038s
# i also borrowed pretty much all of this from kids can code - thanks!
# on acceleration https://www.khanacademy.org/science/physics/one-dimensional-motion/kinematic-formulas/v/average-velocity-for-constant-acceleration 
# on vectors: https://www.youtube.com/watch?v=ml4NSzCQobk 

# dummy comment

import pygame as pg
from pygame.sprite import Sprite
import random
from random import randint, randrange, choice
from settings import *

vec = pg.math.Vector2
class Spritesheet:
    # class for loading and parsing sprite sheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        # image = pg.transform.scale(image, (width // 2, height // 2))
        return image
class Player(Sprite):
    def __init__(self, game):
        # allows layering in LayeredUpdates sprite group - thanks pygame!
        self._layer = PLAYER_LAYER
        # add player to game groups when instantiated
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.flying = False
        self.falling = False
        self.ducking = False
        self.current_frame = 0
        self.last_update = 0
        self.shoot_timer = 0
        self.load_images()
        # self.image = pg.Surface((30,40))
        # self.image = self.game.spritesheet.get_image(614,1063,120,191)
        self.image = self.standing_frames_r[0]
        self.image.set_colorkey(BLACK)
        # self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT /2)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
    def load_images(self):
        self.standing_frames_r = [self.game.spritesheet.get_image(608,495,119,230),
                                self.game.spritesheet.get_image(729,495,119,227)
                                ]
        self.standing_frames_l = []
        for frame in self.standing_frames_r:
            frame.set_colorkey(BLACK)
            self.standing_frames_l.append(pg.transform.flip(frame, True, False))
        self.fly_frames_r = [self.game.spritesheet.get_image(147,199,252,294),
                                self.game.spritesheet.get_image(401,199,254,227),
                                self.game.spritesheet.get_image(657,199,143,210),
                                self.game.spritesheet.get_image(802,199,150,244),
                                self.game.spritesheet.get_image(401,199,254,227)
                                ]
        self.walk_frames_r = [self.game.spritesheet.get_image(850,495,168,225),
                                self.game.spritesheet.get_image(2,752,117,230),
                                self.game.spritesheet.get_image(121,752,170,225),
                                self.game.spritesheet.get_image(293,752,115,231)
                                ]
        '''setup left frames by flipping and appending them into an empty list'''
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        self.fly_frames_l = []
        for frame in self.fly_frames_r:
            frame.set_colorkey(BLACK)
            self.fly_frames_l.append(pg.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(397,196,243,241)
        self.jump_frame.set_colorkey(BLACK)
        self.fall_frame = self.game.spritesheet.get_image(401,199,254,227)
        self.fall_frame.set_colorkey(BLACK)
        self.duck_frame = self.game.spritesheet.get_image(1608,0,243,344)
        self.duck_frame.set_colorkey(BLACK)
        self.aim_right = True
    def update(self):
        now = pg.time.get_ticks()
        self.animate()
        if not self.flying and self.rect.bottom < HEIGHT:
            self.acc = vec(0, PLAYER_GRAV)
        if self.flying == True:
            self.acc = vec(0, 0)
        keys = pg.key.get_pressed()
        # this is where he shoots something
        if keys[pg.K_f]:
            if now - self.shoot_timer > 500:
                Featherblade(self.game, self)
                self.shoot_timer = now
        if keys[pg.K_a]:
            if self.flying:
                self.acc.x = -PLAYER_FLIGHT_ACC
            else:
                self.acc.x =  -PLAYER_ACC
            self.aim_right = False
        if keys[pg.K_d]:
            if self.flying:
                self.acc.x = PLAYER_FLIGHT_ACC
            else:
                self.acc.x = PLAYER_ACC
            self.aim_right = True
        if keys[pg.K_w] and self.flying:
            self.acc.y =  -PLAYER_FLIGHT_ACC
        if keys[pg.K_s] and self.flying:
            self.acc.y =  PLAYER_ACC
        # set player friction
        if not self.flying:
            self.acc.x += self.vel.x * PLAYER_FRICTION
        else:
            self.acc.x += self.vel.x * PLAYER_FLIGHT_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        if self.vel.y > 1 and not self.flying:
            # print(str(self.vel.y) + "current y velocity")
            self.falling = True
        else:
            self.falling = False
        if self.flying:
            self.rect.center = self.pos
        else:
            self.rect.midbottom = self.pos
    # cuts the jump short when the space bar is released
    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -5:
                self.vel.y = -5
    def jump(self):
        # print("jump is working")
        # check pixel below
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        # adjust based on checked pixel
        self.rect.y -= 2
        # only allow jumping if player is on platform
        if hits and not self.jumping or self.pos.y >= HEIGHT:
            # play sound only when space bar is hit and while not jumping
            self.game.jump_sound[choice([0,1])].play()
            # tell the program that player is currently jumping
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            # print("player vel " + str(self.vel.y))
            # print("player pos " + str(self.pos))
    def fly(self):
        # print("fly is working")
        # check pixel below
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        # adjust based on checked pixel
        self.rect.y -= 2
        # only allow jumping if player is on platform
        if hits and not self.jumping or self.pos.y >= HEIGHT:
            # play sound only when space bar is hit and while not jumping
            self.game.jump_sound[choice([0,1])].play()
            # tell the program that player is currently jumping
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            # print("player vel " + str(self.vel.y))
            # print("player pos " + str(self.pos))
    def animate(self):
        # gets time in miliseconds
        now = pg.time.get_ticks()
        # print(str(self.vel.x) + " current vel.x")
        if abs(self.vel.x) > 1.5 and not self.flying:
            self.walking = True
        else:
            self.walking = False
        if self.ducking:
            self.image = self.duck_frame
        if self.jumping:
            self.image = self.jump_frame
        if self.falling:
            self.image = self.fall_frame
        if self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                '''
                assigns current frame based on the next frame and the remaining frames in the list
                using modulus trick
                '''
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 1.5:
                    self.image = self.walk_frames_r[self.current_frame]
                elif self.vel.x < -1.53:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if self.flying:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.fly_frames_l)
                bottom = self.rect.bottom
                if self.current_frame == 0:
                    self.pos.y -=25
                    self.pos.x -=25
                if self.vel.x > 0:
                    self.image = self.fly_frames_r[self.current_frame]
                else:
                    self.image = self.fly_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # checks state
        if not self.jumping and not self.walking and not self.ducking and not self.falling and abs(self.vel.x) < 64:
            # gets current delta time and checks against 200 miliseconds
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames_r)
                # reset bottom for each frame of animation
                bottom = self.rect.bottom
                if self.aim_right == True:
                    self.image = self.standing_frames_r[self.current_frame]
                else:
                    self.image = self.standing_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # collide will find this property if it is called self.mask
        self.mask = pg.mask.from_surface(self.image)
class Cloud(Sprite):
    def __init__(self, game):
        # allows layering in LayeredUpdates sprite group
        self._layer = CLOUD_LAYER
        # add Platforms to game groups when instantiated
        self.groups = game.all_sprites, game.clouds
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange (50, 101) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), 
                                                     int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)
        self.speed = randrange(1,3)
    def update(self):
        if self.rect.top > HEIGHT * 2: 
            self.kill
            ''' mr cozort added animated clouds and made it so they 
            restart on the other side of the screen'''
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.rect.x = -self.rect.width
class Platform(Sprite):
    def __init__(self, game, x, y):
        # allows layering in LayeredUpdates sprite group
        self._layer = PLATFORM_LAYER
        # add Platforms to game groups when instantiated
        self.groups = game.all_sprites, game.platforms
        Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(383,2,159,77),
                  self.game.spritesheet.get_image(544,2,414,84)]
        self.type = ['grass', 'rock']
        if self.type == 'grass':
            self.images = [self.game.spritesheet.get_image(383,2,159,77), 
                  self.game.spritesheet.get_image(544,2,414,84)]
        elif self.type == 'rock':
            self.images = [self.game.spritesheet.get_image(383,2,159,77), 
                  self.game.spritesheet.get_image(544,2,414,84)]
        self.image = random.choice(images)
        self.image.set_colorkey(BLACK)
        '''leftovers from random rectangles before images'''
        # self.image = pg.Surface((w,h))
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)
        if randrange(100) < CACTUS_SPAWN_PCT:
            Cactus(self.game, self)
    def update(self):
        if self.game.score > 500:
            self.type = 'rock'
class Moving_Platform(Sprite):
    def __init__(self, game, x, y):
        # allows layering in LayeredUpdates sprite group
        self._layer = PLATFORM_LAYER
        # add Platforms to game groups when instantiated
        self.groups = game.all_sprites, game.mplatforms
        Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(383,2,159,77),
                  self.game.spritesheet.get_image(544,2,414,84)]
        self.type = ['grass', 'rock']
        if self.type == 'grass':
            self.images = [self.game.spritesheet.get_image(383,2,159,77), 
                  self.game.spritesheet.get_image(544,2,414,84)]
        elif self.type == 'rock':
            self.images = [self.game.spritesheet.get_image(383,2,159,77), 
                  self.game.spritesheet.get_image(544,2,414,84)]
        self.image = random.choice(images)
        self.image.set_colorkey(BLACK)
        '''leftovers from random rectangles before images'''
        # self.image = pg.Surface((w,h))
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = 5
        if randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)
        if randrange(100) < CACTUS_SPAWN_PCT:
            Cactus(self.game, self)
    def update(self):
        self.rect.x += self.vx
        if self.rect.x > WIDTH or self.rect.x < 0:
            self.kill
        if self.game.score > 500:
            self.type = 'rock'
class Ground(Sprite):
    def __init__(self, game, screen):
        # allows layering in LayeredUpdates sprite group
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.screen = screen
        # self.image = pg.Surface((WIDTH,25))
        # self.image.fill(WHITE)
        self.image = self.game.ground_image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rel_x = self.rect.x % self.rect.width
        self.rect.y = HEIGHT - self.rect.height
        self.shift = 0
    def update(self):
        self.rect.x -= self.game.player.vel.x
        self.blitme()
    def blitme(self):
        self.screen.blit(self.image, (self.rect.x+WIDTH, self.rect.y))
class Pow(Sprite):
    def __init__(self, game, plat):
        # allows layering in LayeredUpdates sprite group
        self._layer = POW_LAYER
        # add a groups property where we can pass all instances of this object into game groups
        self.groups = game.all_sprites, game.powerups
        Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['boost', 'slow'])
        self.image = self.game.spritesheet.get_image(2,199,143,27)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        # checks to see if plat is in the game's platforms group so we can kill the powerup instance
        if not self.game.platforms.has(self.plat):
            self.kill()
class Featherblade(Sprite):
    def __init__(self, game, player):
        # allows layering in LayeredUpdates sprite group
        self._layer = POW_LAYER
        # add a groups property where we can pass all instances of this object into game groups
        self.groups = game.all_sprites, game.featherblades
        Sprite.__init__(self, self.groups)
        self.game = game
        self.player = player
        self.type = ['boost']
        self.image = self.game.spritesheet.get_image(2,199,143,27)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.player.rect.centerx
        self.rect.bottom = self.player.rect.top - 5
        self.vx = 25
        if self.player.aim_right == False:
            print("should be shooting left...")
            self.image = pg.transform.flip(self.image, True, False)
            self.vx *= -1
        self.vy = 0
        print("im alive!")
    def update(self):
        self.rect.x += self.vx
        center = self.rect.center
        # animation based on change in y value
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect_top = self.rect.top
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()
class Mob(Sprite):
    def __init__(self, game):
        # allows layering in LayeredUpdates sprite group
        self._layer = MOB_LAYER
        # add a groups property where we can pass all instances of this object into game groups
        self.groups = game.all_sprites, game.mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(75,2,152,147)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(229,2,152,195)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        # self.rect.centerx = randrange(0, WIDTH)
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT//1.5)
        self.vy = 0
        self.dy = 0.5
    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or  self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        # animation based on change in y value
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect_top = self.rect.top
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()
class Cactus(Sprite):
    def __init__(self, game, plat):
        # allows layering in LayeredUpdates sprite group
        self._layer = POW_LAYER
        # add a groups property where we can pass all instances of this object into game groups
        self.groups = game.all_sprites, game.cacti
        Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.image = self.game.spritesheet.get_image(2,2,71,79)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        # checks to see if plat is in the game's platforms group so we can kill the powerup instance
        if not self.game.platforms.has(self.plat):
            self.kill()