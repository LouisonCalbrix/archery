#! /usr/bin/env python3

# program: the super tiny bow game
# This is a mini game where you press the space bar to shoot an arrow at a target
# author: Louison Calbrix
# date: December 2019

import os
import pygame

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 650
SCORE_TABLE = [3, 2, 1]
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

class Bow(pygame.sprite.Sprite):
    '''
    A bow moving across the screen from top to bottom and back.
    It can shoot arrows.
    '''

    IMG = pygame.image.load('resources/bow.png')
    ROPE_TOP = (54, 20)
    ROPE_BOT = (54, 180)
    ROPE_STATES = 10
    AMMO_MAX = 5
    SPEED = [0, 8]
    FORCE_MIN = 10
    FORCE_MAX = 50
    TIME_FORCE_S = 0.7
    TIME_COOLDOWN_S = 1
    INSTANCE = pygame.sprite.GroupSingle()

    def __init__(self, player):
        '''
        Create a Bow.
        '''
        super().__init__()
        self.draw(0)
        self._rect = self._img.get_rect()
        self._rect.move_ip(20, 0)
        self._bent_time = 0
        self._cooldown = 0
        self._speed = Bow.SPEED.copy()
        self._arrow = Arrow
        self._ammo = Bow.AMMO_MAX
        self._player = player
        Bow.INSTANCE.add(self)

    def update(self):
        '''
        Update bow's position and potentially handle the cooldown.
        '''
        self._rect.move_ip(*self._speed)
        if self._rect.y < 0 or self._rect.y > SCREEN_HEIGHT-self._rect.height:
            self._speed = [-speed_component for speed_component in self._speed]
        if self._cooldown:
            self._cooldown -= 1
            if self._cooldown == 0 and self._ammo:
                self.draw(0)
        if 0 < self._bent_time < Bow.TIME_FORCE_FPS:
            self._bent_time += 1
            step = self._bent_time / (Bow.TIME_FORCE_FPS // Bow.ROPE_STATES)
            if step.is_integer():
                self.draw(step)

    def bend(self):
        '''
        Bend the bow, a bow needs to be bent to shoot an arrow.
        '''
        if not self._cooldown and self._ammo:
            self._bent_time += 1

    def shoot(self):
        '''
        Shoot an arrow, when the pressure of a bent bow is release, an arrow
        is shot.
        '''
        if self._bent_time:
            self._arrow(self._player, self._rect.copy(), self.force)
            self._ammo -= 1
            self._bent_time = 0
            self._cooldown = Bow.TIME_COOLDOWN_FPS
            self.draw(-1)

    def draw(self, step):
        '''
        Draw the bow, only to be called when the bow's state changes.
        '''
        self._img = Bow.IMG.copy()
        overlay = pygame.Surface(Bow.IMG.get_size())
        if step == -1:
            pygame.draw.line(overlay, (255, 255, 255), Bow.ROPE_TOP, Bow.ROPE_BOT)
        else:
            base_x = Bow.ROPE_TOP[0]
            x = base_x * (1 - step / Bow.ROPE_STATES)
            pygame.draw.line(overlay, (255, 255, 255), Bow.ROPE_TOP, (x, Bow.ROPE_MIDDLE))
            pygame.draw.line(overlay, (255, 255, 255), Bow.ROPE_BOT, (x, Bow.ROPE_MIDDLE))
            overlay.blit(Arrow.IMG, (x - base_x, 0))
        overlay.set_colorkey(overlay.get_at((0, 0)))
        self._img.blit(overlay, (0, 0))


    @property
    def force(self):
        return ((Bow.FORCE_MAX-Bow.FORCE_MIN) / Bow.TIME_FORCE_FPS) * self._bent_time + Bow.FORCE_MIN

    @property
    def image(self):
        return self._img

    @property
    def rect(self):
        return self._rect

    @classmethod
    def init(cls, fps):
        '''
        Initialize pictures that represent an instance of Bow onscreen. Not to
        be called before pygame image module has been initialized.
        '''
        cls.IMG.set_colorkey(cls.IMG.get_at((0, 0)))
        cls.IMG = cls.IMG.convert()
        cls.FPS = fps
        cls.TIME_COOLDOWN_FPS = int(cls.TIME_COOLDOWN_S * cls.FPS)
        cls.TIME_FORCE_FPS = int(cls.TIME_FORCE_S * cls.FPS)
        cls.ROPE_MIDDLE = ((cls.ROPE_BOT[1] - cls.ROPE_TOP[1]) // 2) + cls.ROPE_TOP[1]


class Arrow(pygame.sprite.Sprite):
    '''
    An arrow that can be shot by a bow. It has an horizontal speed, that makes
    it move across the screen from left to right. It is destroyed if it goes
    beyond the screen's boundaries.
    '''
    IMG = pygame.image.load('resources/arrow.png')
    IMG_HIT = pygame.image.load('resources/arrow_stopped.png')
    SPEED = [15, 0]
    INSTANCES = pygame.sprite.Group()
    HITBOX_OFFSET = (165, 90)
    HITBOX_SIZE = (26, 17)

    def __init__(self, player, bow_rect, force):
        '''
        Create an arrow that is shot by a bow whose position is represented by
        bow_rect.
        '''
        print('shot arrow {}'.format(force))
        super().__init__()
        self._bow = bow
        self._img = Arrow.IMG
        self._rect = bow_rect
        self._speed = [force, 0]
        x, y = self._rect.x, self._rect.y
        hit_coords = [coord+offset for coord, offset in zip((x, y), Arrow.HITBOX_OFFSET)]
        self._hitbox = pygame.Rect(hit_coords, Arrow.HITBOX_SIZE)
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
                self._img = Arrow.IMG_HIT
                self._score = SCORE_TABLE[hit]
                self._player.update_score(self)

    # test
    def __del__(self):
        print('deleted arrow')

    @property
    def image(self):
        return self._img

    @property
    def rect(self):
        return self._rect

    @property
    def score(self):
        return self._score

    @classmethod
    def init(cls, background):
        '''
        Initialize the picture for future Arrow objects. Since method calls 
        in here require pygame's image module to be initialized, this class
        method should not be called before pygame.init().
        '''
        cls.IMG = cls.IMG.convert()
        cls.IMG.set_colorkey(cls.IMG.get_at((0, 0)))
        cls.IMG_HIT = cls.IMG_HIT.convert()
        cls.IMG_HIT.set_colorkey(cls.IMG_HIT.get_at((0, 0)))
        cls.BACKGROUND = background


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
    background.blit(img, pos)

# for test purpose
if __name__ == '__main__':
    
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fps = 30
    background = pygame.image.load('resources/background.png')

    # Bow and Arrow init
    Bow.init(fps)
    Arrow.init(background)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bow.bend()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    bow.shoot()
        onscreen_sprites.update_draw()
        score_surface = font.render(str(player.score), False, (0, 255, 0))
        screen.blit(background, (SCREEN_WIDTH//2, 0),
                    pygame.Rect((SCREEN_WIDTH//2, 0), font.size(str(player.score))))
        screen.blit(score_surface, (SCREEN_WIDTH//2, 0))
        pygame.display.flip()
        clock.tick(fps)


