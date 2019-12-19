#! /usr/bin/env python3

# program: the super tiny bow game
# This is a mini game where you press the space bar to shoot an arrow at a target
# author: Louison Calbrix
# date: December 2019

import os
import pygame
import random

#----------constants

# screen and display
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 650
LIGHTNESS_SKY_MAX = 90
COLOR_SKY = pygame.Color(80, 80, 200)
COLOR_GRASS = pygame.Color(70, 200, 70)

# game score
SCORE_TABLE = [3, 2, 1]
# game "physics"
GRAVITY = 3

class Player:
    def __init__(self):
        self._score = 0

    def update_score(self, arrow):
        self._score += arrow.score
        print('updated score: {}'.format(self._score))

    @property
    def score(self):
        return self._score


class GameObject(pygame.sprite.Sprite):
    '''
    Super class for any game element that eventually gets drawn onscreen and
    that may be moved around.
    '''

    def __init__(self, img, topleft, speed):
        '''
        Initialize game object with:
            img being its picture onscreen and 
            rect its position
            speed a list of two integers that makes the game object move
             every frame.
        '''
        super().__init__()
        self._img = img
        self._rect = img.get_rect()
        self._rect.move_ip(topleft)
        self._speed = speed

    def update(self):
        '''
        Empty method. Subclass needs to override this.
        '''
        raise NotImplementedError()

    @property
    def image(self):
        ''' image(self) -> self._img'''
        return self._img

    @property
    def rect(self):
        ''' rect(self) -> self._rect'''
        return self._rect

    @classmethod
    def init(cls):
        '''
        Initialize pictures that were loaded by the subclass to represent said
        class instances onscreen. Subclasses need to load these pictures in a
        class attribute named IMGS that is a list of Surfaces likewise:
            IMGS = [
                pygame.image.load('resources/img1.png'),
                pygame.image.load('resources/img2.png'),
                ...
            ]
        Implementation advice: use named indices such as:
            IDDLE = 0
            RUNNING = 1
            ...
        So that later uses of IMGS are explicit:
            cls.IMGS[cls.IDDLE]
        Not to be called before pygame image modulea has been initialized.
        '''
        IMGS = []
        for surface in cls.IMGS:
            colorkey = surface.get_at((0, 0))
            surface.set_colorkey(colorkey)
            surface = surface.convert()
            IMGS.append(surface)
        cls.IMGS = IMGS


class Bow(GameObject):
    '''
    A bow moving across the screen from top to bottom and back.
    It can shoot arrows.
    '''

    # picture for bow onscreen
    IMGS = [pygame.image.load('resources/bow2.png')]
    # drawing markers
    ROPE_TOP = (54, 20)
    ROPE_BOT = (54, 180)
    # animation
    ROPE_STATES = 10
    # misc constants
    SPEED = [0, 8]
    AMMO_MAX = 5
    FORCE_MIN = 10
    FORCE_MAX = 50
    TIME_FORCE_S = 0.7
    TIME_COOLDOWN_S = 1
    # class attribute keeping track of instances of the class
    INSTANCE = pygame.sprite.GroupSingle()

    def __init__(self, player):
        '''
        Create a Bow.
        '''
        super().__init__(Bow.IMGS[0],
                         (20, 0),
                         Bow.SPEED.copy())
        self._state = NormalBowState(self)
        self._arrow = Arrow
        self._ammo = Bow.AMMO_MAX
        self._player = player
        Bow.INSTANCE.add(self)

    def update(self, inputs):
        '''
        Update bow's position and potentially handle the cooldown.
        '''
        self._rect.move_ip(*self._speed)
        if self._rect.y < 0 or self._rect.y > SCREEN_HEIGHT-self._rect.height:
            self._speed = [-speed_component for speed_component in self._speed]
        self._state.update(inputs)

    def shoot(self):
        '''
        Shoot an arrow, when the pressure of a bent bow is release, an arrow
        is shot.
        '''
        topleft = self._rect.topleft
        self._arrow(self._player, topleft, self.force)
        self._ammo -= 1

    def draw(self, step):
        '''
        Draw the bow, only to be called when the bow's state changes.
        '''
        rope_color = (255, 255, 255)
        self._img = Bow.IMGS[0].copy()
        overlay = pygame.Surface(self._img.get_size())
        if step == -1:
            pygame.draw.line(overlay, rope_color, Bow.ROPE_TOP, Bow.ROPE_BOT)
        else:
            base_x = Bow.ROPE_TOP[0]
            x = base_x * (1 - step / Bow.ROPE_STATES)
            pygame.draw.line(overlay, rope_color, Bow.ROPE_TOP, (x, Bow.ROPE_MIDDLE))
            pygame.draw.line(overlay, rope_color, Bow.ROPE_BOT, (x, Bow.ROPE_MIDDLE))
            overlay.blit(Arrow.IMGS[Arrow.SHOT], (x - base_x, 0))
        overlay.set_colorkey(overlay.get_at((0, 0)))
        self._img.blit(overlay, (0, 0))


    @property
    def force(self):
        return ((Bow.FORCE_MAX-Bow.FORCE_MIN) / Bow.TIME_FORCE_FPS) * self._bent_time + Bow.FORCE_MIN

    @classmethod
    def init(cls, fps):
        '''
        Initialize pictures that represent an instance of Bow onscreen. Not to
        be called before pygame image module has been initialized.
        '''
        super().init()
        cls.TIME_COOLDOWN_FPS = int(cls.TIME_COOLDOWN_S * fps)
        cls.TIME_FORCE_FPS = int(cls.TIME_FORCE_S * fps)
        cls.ROPE_MIDDLE = ((cls.ROPE_BOT[1] - cls.ROPE_TOP[1]) // 2) + cls.ROPE_TOP[1]


class NormalBowState:
    '''
    State for bow instances.
    '''
    def __init__(self, master):
        self._master = master
        self._master.draw(0)

    def update(self, inputs):
        for an_input in inputs:
            if an_input.type == pygame.KEYDOWN:
                if an_input.key == pygame.K_SPACE:
                    self._master._state = BentBowState(self._master)


class BentBowState:
    '''
    State for bow instances.
    '''
    def __init__(self, master):
        self._master = master
        self._master._bent_time = 0

    def update(self, inputs):
        if self._master._bent_time < Bow.TIME_FORCE_FPS:
            self._master._bent_time += 1
            step = self._master._bent_time / (Bow.TIME_FORCE_FPS // Bow.ROPE_STATES)
            if step.is_integer():
                self._master.draw(step)
        for an_input in inputs:
            if an_input.type == pygame.KEYUP:
                if an_input.key == pygame.K_SPACE:
                    self._master.shoot()
                    if self._master._ammo:
                        self._master._state = ReloadBowState(self._master)
                    else:
                        self._master._state = EmptyBowState(self._master)


class ReloadBowState:
    '''
    State for bow instances.
    '''
    def __init__(self, master):
        self._master = master
        self._master.draw(-1)
        self._master._cooldown = Bow.TIME_COOLDOWN_FPS

    def update(self, inputs):
        self._master._cooldown -= 1
        if self._master._cooldown == 0:
            self._master._state = NormalBowState(self._master)


class EmptyBowState:
    '''
    State for bow instances.
    '''
    def __init__(self, master):
        self._master = master
        self._master.draw(-1)
        self._master._speed = [0, 0]

    def update(self, inputs):
        pass


class Arrow(GameObject):
    '''
    An arrow that can be shot by a bow. It has an horizontal speed, that makes
    it move across the screen from left to right. It is destroyed if it goes
    beyond the screen's boundaries.
    '''
    IMGS = [
        pygame.image.load('resources/arrow2.png'),
        pygame.image.load('resources/arrow_stopped2.png')
    ]
    SHOT = 0
    STOPPED = 1
    INSTANCES = pygame.sprite.Group()
    HITBOX_OFFSET = (165, 90)
    HITBOX_SIZE = (26, 17)

    def __init__(self, player, topleft, force):
        '''
        Create an arrow that is shot by a bow whose position is represented by
        bow_rect.
        '''
        super().__init__(Arrow.IMGS[Arrow.SHOT],
                         topleft,
                         [force, 0])

        x, y = self._rect.x, self._rect.y
        self._hitbox = pygame.Rect((x, y), Arrow.HITBOX_SIZE)
        self._hitbox.move_ip(*Arrow.HITBOX_OFFSET)
        self._target = Target.INSTANCE
        self._player = player
        self._score = 0
        Arrow.INSTANCES.add(self)

    def update(self):
        '''
        Update a moving arrow's position.
        '''
        if self._speed != [0, 0]:
            self._speed[1] += GRAVITY
            self._rect.move_ip(self._speed)
            self._hitbox.move_ip(self._speed)
            if self._rect.x > SCREEN_WIDTH or self._rect.y > SCREEN_HEIGHT:
                super().kill()
            hit = self._hitbox.collidelist(self._target.hitbox)
            if hit != -1:
                self._speed = [0, 0]
                self._img = Arrow.IMGS[Arrow.STOPPED]
                self._score = SCORE_TABLE[hit]
                self._player.update_score(self)

    def __del__(self):
        print('deleted arrow')

    @property
    def score(self):
        return self._score


class Target:
    '''
    Target that needs to be hit.
    '''
    OUTER_I = 2
    MIDDLE_I = 1
    INNER_I = 0
    AREAS = [
        ((79, 127), (26, 153)),
        ((88, 59), (34, 289)),
        ((88, 0), (42, 399))
    ]
    IMG = pygame.image.load('resources/target.png')
    INSTANCE = None

    def __init__(self, background):
        '''
        '''
        super().__init__()
        Target.INSTANCE = self
        img = Target.IMG
        x = SCREEN_WIDTH - img.get_width()
        y = SCREEN_HEIGHT - img.get_height()
        iddle_sprite(Target.IMG, (x, y), background)

        inner = Target.AREAS[Target.INNER_I]
        self._inner_hit = pygame.Rect(inner[0], inner[1])
        self._inner_hit.move_ip(x, y)
        middle = Target.AREAS[Target.MIDDLE_I]
        self._middle_hit = pygame.Rect(middle[0], middle[1])
        self._middle_hit.move_ip(x, y)
        outer = Target.AREAS[Target.OUTER_I]
        self._outer_hit = pygame.Rect(outer[0], outer[1])
        self._outer_hit.move_ip(x, y)

    @property
    def image(self):
        return self._img

    @property
    def rect(self):
        return self._rect

    @property
    def hitbox(self):
        return self._inner_hit, self._middle_hit, self._outer_hit

    @classmethod
    def init(cls):
        '''
        Initialize pictures that represent an instance of Target onscreen. Not to
        be called before pygame image module has been initialized.
        '''
        cls.IMG = cls.IMG.convert()
        cls.IMG.set_colorkey(cls.IMG.get_at((0, 0)))


class DisplayGroup(pygame.sprite.OrderedUpdates):
    '''
    Class whose purpose is to draw every game object on the screen.
    '''

    def __init__(self, screen, background, *groups):
        '''
        Initialize a display group. groups are expected to be pygame.sprite.Group,
        or subclass.
        '''
        super().__init__()
        self._screen = screen
        self._background = background
        self._groups = groups
        for group in self._groups:
            super().add(group.sprites())

    def update_draw(self):
        for group in self._groups:
            for sprite in group.sprites():
                if sprite not in self:
                    super().add(sprite) 
        super().clear(self._screen, self._background)
        super().update()
        super().draw(self._screen)


def iddle_sprite(img, pos, background):
    '''
    Draw img at pos on the background, thus changing the background.
    '''
    background.blit(img, pos)

def darken_color(base_color, current_color, counter):
    '''
    Randomly return a darken color or the base_color depending on counter,
    the highest counter is the less likely a darker color will be returned.
    '''
    prob = 15 + counter
    rand = random.randint(0, prob)
    if rand >= prob-17:
        # darken
        h, s, l, a = current_color.hsla
        l *= 0.70
        current_color.hsla = h, s, l, a
        return current_color, counter+1
    else:
        return pygame.Color(*base_color), 0

def draw_background(size, sky_stripes=1):
    # background creation
    background = pygame.Surface(size)
    b_width, b_height = size
    # draw sky
    sky_height = b_height / 2
    height_step = sky_height // sky_stripes 
    stripe_color = pygame.Color(*COLOR_SKY)
    h, s, l, a = stripe_color.hsla
    l_step = (LIGHTNESS_SKY_MAX - l) / sky_stripes
    sky_stripe = pygame.Rect(0, 0, b_width, height_step)
    for i in range(sky_stripes):
        pygame.draw.rect(background, stripe_color, sky_stripe)
        sky_stripe.move_ip(0, height_step)
        l += l_step
        stripe_color.hsla = h, s, l, a
    # draw grass
    sky_bottom = int((i+1) * height_step)
    px_array = pygame.PixelArray(background)
    current_color = pygame.Color(*COLOR_GRASS)
    counter = 0
    for i in range(b_width):
        for j in range(sky_bottom, b_height):
#        for j in range(b_height-1, sky_bottom-1, -1):
            current_color, counter = darken_color(COLOR_GRASS, current_color, counter)
            px_array[i, j] = current_color
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    return background


# for test purpose
if __name__ == '__main__':
    
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fps = 30
    background = draw_background((200, 240), 8)
#    background = pygame.image.load('resources/background.png').convert()

    # Bow and Arrow init
    Bow.init(fps)
    Arrow.init()
    Target.init()
    # Bow instanciation
    player = Player()
    bow = Bow(player)
    target = Target(background)
    onscreen_sprites = DisplayGroup(screen,
                                    background,
                                    Bow.INSTANCE, Arrow.INSTANCES)

    font = pygame.font.Font(None, 55)
    screen.blit(background, (0, 0))
    while True:
        for group in Bow.INSTANCE, Arrow.INSTANCES:
            group.clear(screen, background)
        inputs = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                inputs.append(event)
            elif event.type == pygame.KEYUP:
                inputs.append(event)
        Bow.INSTANCE.sprite.update(inputs)
        Arrow.INSTANCES.update()
        for group in Bow.INSTANCE, Arrow.INSTANCES:
            group.draw(screen)
#        onscreen_sprites.update_draw(inputs)
        score_surface = font.render(str(player.score), False, (0, 255, 0))
        screen.blit(background, (SCREEN_WIDTH//2, 0),
                    pygame.Rect((SCREEN_WIDTH//2, 0), font.size(str(player.score))))
        screen.blit(score_surface, (SCREEN_WIDTH//2, 0))
        pygame.display.flip()
        clock.tick(fps)


