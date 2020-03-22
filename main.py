# this file was created by Chris Cozort
# Sources: goo.gl/2KMivS - thanks Chris Bradfield!
# now available in github

'''
Curious, Creative, Tenacious(requires hopefulness)

**********Gameplay ideas:
Shoot feathers out of wings to dFefeat enemies
Health bar

**********Cosmetics
Change hero images (5 images), platforms, clouds, enemies(2 images), bg image? DONE

**********Bugs
when you get launched by powerup or head jump player sometimes snaps to platform abruptly 
happens when hitting jump during power up boost

**********Gameplay fixes
Platform randomness leaves player in limbo for extended periods
Lower spawn location so player can get out of random stuck situations

**********Features
Varied powerups that add ammo to your feather
'''
import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    ##### INIT METHOD
    def __init__(self):
        #init game window
        # init pygame and create window
        pg.init()
        # init sound mixer
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("jumpy")
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
    ##### LOAD DATA METHOD
    def load_data(self):
        # print("load data is called...")
        # sets up directory name for images
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        # opens file with write options
        ''' with is a contextual option that handles both opening and closing of files to avoid
        issues with forgetting to close
        '''
        try:
            # changed to r to avoid overwriting error
            with open(path.join(self.dir, "highscore.txt"), 'r') as f:
                self.highscore = int(f.read())
                # print(self.highscore)
        except:
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                self.highscore = 0
                print("exception")
        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET)) 
        #load cloud images
        self.cloud_images = []
        for i in range(1,4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())
        self.ground_image = pg.image.load(path.join(img_dir, 'ground.png')).convert()
        self.ground_rect = self.ground_image.get_rect()
        self.g_scroll_start = 0
        # load sounds
        # great place for creating sounds: https://www.bfxr.net/
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = [pg.mixer.Sound(path.join(self.snd_dir, 'Jump18.wav')),
                            pg.mixer.Sound(path.join(self.snd_dir, 'Jump24.wav'))]
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump29.wav'))
        self.head_jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump39.wav'))
    ##### NEW METHOD
    def new(self):
        self.score = 0
        self.paused = False
        # add all sprites to the pg group
        # below no longer needed - using LayeredUpdate group
        # self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        # create platforms group
        self.platforms = pg.sprite.Group()
        # create mplatforms group
        self.platforms = pg.sprite.Group()
        # create ground
        # create clouds group
        self.clouds = pg.sprite.Group()
        # add powerups
        self.powerups = pg.sprite.Group()
        # add cacti
        self.cacti = pg.sprite.Group()
        self.mob_timer = 0
        # add a player 1 to the group
        self.player = Player(self)
        # add a player 1 to the group
        self.featherblades = pg.sprite.Group()
        self.ground = Ground(self, self.screen)
        # add mobs
        self.mobs = pg.sprite.Group()
        # no longer needed after passing self.groups in Sprites library file
        # self.all_sprites.add(self.player)
        # instantiate new platform 
        for plat in PLATFORM_LIST:
            # no longer need to assign to variable because we're passing self.groups in Sprite library
            # p = Platform(self, *plat)
            Platform(self, *plat)
        # for plat in MOVEPLAT_LIST:
        #     # no longer need to assign to variable because we're passing self.groups in Sprite library
        #     # p = Platform(self, *plat)
        #     Moveplat(self, *plat)

        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500
        # load music
        # pg.mixer.music.load(path.join(self.snd_dir, 'happy.ogg'))
        # call the run method
        self.run()
    ##### RUN METHOD
    def run(self):
        # game loop
        # play music
        # pg.mixer.music.play(loops=-1)
        # set boolean playing to true
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        # pg.mixer.music.fadeout(1000)
        # other things that happen when not playing anymore
    ##### UPDATE METHOD
    def update(self):
        self.all_sprites.update()
        now = pg.time.get_ticks()
        # scroll ground
        self.rel_g_start =  self.g_scroll_start % self.ground_rect.width
        self.screen.blit(self.ground_image, (self.rel_g_start - self.ground_rect.width, HEIGHT-50))
        if self.rel_g_start < WIDTH:
            self.screen.blit(self.ground_image, (self.rel_g_start, HEIGHT-50)) 
        # detect the ground or ceiling
        self.player.rect.y += 2
        if self.player.pos.y >= HEIGHT:
            # print("Flying " + str(self.player.flying))
            self.player.vel.y = 0
            self.player.pos.y = HEIGHT-150
            self.player.jumping = False
            # print("should be stopping")
        elif self.player.pos.y <= 225:
            self.player.vel.y = 0
            # print("should be stopping then falling...")
        self.player.rect.y -= 2
        # shall we spawn a mob?
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # check for feather collisions
        # now using collision mask to determine collisions
        # can use rectangle collisions here first if we encounter performance issues
        feather_hits = pg.sprite.groupcollide(self.mobs, self.featherblades, False, False)
        if feather_hits:
            feather_mask_hits = pg.sprite.groupcollide(self.mobs, self.featherblades, True, True, pg.sprite.collide_mask)
            if feather_mask_hits:
                print("That's great kid, don't get cocky...")
        # check for mob collisions
        # now using collision mask to determine collisions
        # can use rectangle collisions here first if we encounter performance issues
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            mob_mask_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
            if mob_mask_hits:
                # can use mask collide here if mob count gets too high and creates performance issues
                ''' I created the below code as an added feature:
                    I wanted to create an option to jump on the enemies'
                    heads to prevent getting stuck...'''
                if self.player.pos.y - 35 < mob_hits[0].rect.top:
                    # print("hit top")
                    print("player is " + str(self.player.pos.y))
                    print("mob is " + str(mob_hits[0].rect.top))
                    # self.head_jump_sound.play()
                    # self.player.vel.y = -BOOST_POWER
                else:
                    print("player is " + str(self.player.pos.y))
                    print("mob is " + str(mob_hits[0].rect.top))
                    # self.playing = False
        # check to see if player collides with plats and can jump - if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                ''' set var to be current hit in list to find which to 'pop' to 
                when two or more collide with player'''
                find_lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > find_lowest.rect.bottom:
                        # print("hit rect bottom " + str(hit.rect.bottom))
                        find_lowest = hit
                # fall if center is off platform
                if self.player.pos.x < find_lowest.rect.right + 5 and self.player.pos.x > find_lowest.rect.left - 5:
                    if self.player.pos.y < find_lowest.rect.centery:
                        self.player.pos.y = find_lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False
                        # print(str(self.player.vel.x) + " vel x from main...")
            # check for on ground
        # control HORIZONTAL scrolling updates
        # if player reaches right left 1/4 of screen...
        if self.player.pos.x >= WIDTH / 1.25:
            self.player.pos.x = WIDTH / 1.25
            # spawn a cloud
            if randrange(100) < 13:
                Cloud(self)
            # set player location based on velocity
            self.player.pos.x += self.player.vel.x
            for cloud in self.clouds:
                cloud.rect.x -= self.player.vel.x / randrange(2,10)
            # creates slight scroll at the top based on player y velocity
            # scroll platswith player
            for cactus in self.cacti:
                # creates slight scroll based on player y velocity
                cactus.rect.x -= self.player.vel.x
            for plat in self.platforms:
                # creates slight scroll based on player y velocity
                plat.rect.x -= self.player.vel.x
                if plat.rect.right <= 0:
                    plat.kill()
                    self.score += 10
        # if player hits a power up
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                # self.player.vel.y = -BOOST_POWER
                # self.player.jumping = False
        cacti_hits = pg.sprite.spritecollide(self.player, self.cacti, False)
        if cacti_hits:    
            if self.player.vel.x > 0 and self.player.pos.x > cacti_hits[0].rect.top:
                    # print("falling")
                    print("player is " + str(self.player.pos.x))
                    print("mob is " + str(cacti_hits[0].rect.top))
          # generate new random platforms
        # this is where new plats are generated
        while len(self.platforms) <  5:
            ''' removed widths and height params to allow for sprites '''
            """ changed due to passing into groups through sprites lib file """
            # p = Platform(self, random.randrange(0,WIDTH-width), 
            #                 random.randrange(-75, -30))
            if self.player.rect.x > WIDTH / 2:
                for i in range(5):
                    Platform(self, random.randrange(0,WIDTH + 1000), 
                                random.randrange(HEIGHT/2, HEIGHT ))
    ##### EVENTS METHOD
    def events(self):
        for event in pg.event.get():
                now = pg.time.get_ticks()
                flytimer = 200 
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        if self.player.flying == True:
                            self.player.flying = False
                            # print("Flying " + str(self.player.flying))
                        else:
                            self.player.flying = True
                            # print("Flying " + str(self.player.flying))
                # if event.type == pg.KEYUP:
                #     if event.key == pg.K_SPACE:
                #         """ # cuts the jump short if the space bar is released """
                #         self.player.jump_cut()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        """ pause """
                        self.paused = True
    ##### DRAW METHOD
    def draw(self):
        self.screen.fill(SKY_BLUE)
        self.all_sprites.draw(self.screen)
        """ # not needed now that we're using LayeredUpdates """
        # self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # double buffering - renders a frame "behind" the displayed frame
        pg.display.flip()
    ##### WAIT FOR KEY METHOD
    def wait_for_key(self): 
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type ==pg.KEYUP:
                    waiting = False
    ##### SHOW START SCREEN METHOD
    def show_start_screen(self):
        """ # game splash screen """
        self.screen.fill(BLACK)
        self.draw_text(TITLE, 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("WASD to move, Space to jump", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press any key to play...", 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
        self.draw_text("High score " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
    ##### SHOW GO SCREEN METHOD
    def show_go_screen(self):
        """ # game splash screen """
        if not self.running:
            print("not running...")
            return
        self.screen.fill(BLACK)
        self.draw_text(TITLE, 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("WASD to move, Space to jump", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press any key to play...", 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
        self.draw_text("High score " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT/2 + 40)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("new high score!", 22, WHITE, WIDTH / 2, HEIGHT/2 + 60)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))

        else:
            self.draw_text("High score " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT/2 + 40)


        pg.display.flip()
        self.wait_for_key()
    ##### DRAW TEXT METHOD
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()

g.show_start_screen()

while g.running:
    g.new()
    try:
        g.show_go_screen()
    except:
        print("can't load go screen...")