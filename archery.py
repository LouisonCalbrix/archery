#! /usr/bin/env python3

# program: the super tiny bow game
# This is a mini game where you press the space bar to shoot an arrow at a target
# author: Louison Calbrix
# date: December 2019

import os
import pygame

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 650

class Bow(pygame.sprite.Sprite):
    '''
    A bow moving across the screen from top to bottom and back.
    It can shoot arrows.
    '''

    IMG_STRAIGHT = pygame.image.load('resources/bow1.png')
    IMG_BENT = pygame.image.load('resources/bow2.png')
    SPEED = [0, 8]
    INSTANCES = pygame.sprite.Group()

    def __init__(self):
        '''
        Create a Bow.
        '''
        super().__init__()
        self._img = Bow.IMG_STRAIGHT
        self._rect = self._img.get_rect()
        self._rect.move_ip(20, 0)
        self._bent = False
        self._speed = Bow.SPEED.copy()
        self._arrow = Arrow
        Bow.INSTANCES.add(self)

    def update(self):
        '''
        Update bow's position, and whether or not an arrow is shot.
        '''
        self._rect.move_ip(*self._speed)
        if self._rect.y < 0 or self._rect.y > SCREEN_HEIGHT-self._rect.height:
            self._speed = [-speed_component for speed_component in self._speed]

    def bend(self):
        '''
        Bend the bow, a bow needs to be bent to shoot an arrow.
        '''
        self._bent = True
        self._img = Bow.IMG_BENT

    def shoot(self):
        '''
        Shoot an arrow, when the pressure of a bent bow is release, an arrow
        is shot.
        '''
        self._bent = False
        self._img = Bow.IMG_STRAIGHT
        self._arrow(self._rect)

    @property
    def image(self):
        return self._img

    @property
    def rect(self):
        return self._rect

    @classmethod
    def init(cls):
        '''
        Initialize pictures that represent an instance of Bow onscreen. Not to
        be called before pygame image module has been initialized.
        '''
        cls.IMG_STRAIGHT.set_colorkey(cls.IMG_STRAIGHT.get_at((0, 0)))
        cls.IMG_STRAIGHT = cls.IMG_STRAIGHT.convert()
        cls.IMG_BENT.set_colorkey(cls.IMG_BENT.get_at((0, 0)))
        cls.IMG_BENT = cls.IMG_BENT.convert()


class Arrow(pygame.sprite.Sprite):
    '''
    An arrow that can be shot by a bow. It has an horizontal speed, that makes
    it move across the screen from left to right. It is destroyed if it goes
    beyond the screen's boundaries.
    '''
    IMG = pygame.image.load('resources/arrow.png')
    SPEED = [15, 0]
    INSTANCES = pygame.sprite.Group()

    def __init__(self, bow_rect):
        '''
        Create an arrow that is shot by a bow whose position is represented by
        bow_rect.
        '''
        super().__init__()
        self._img = Arrow.IMG
        self._rect = bow_rect.copy()
        self._speed = Arrow.SPEED
        Arrow.INSTANCES.add(self)

    def update(self):
        '''
        Update a moving arrow's position.
        '''
        self._rect.move_ip(self._speed)
        if self._rect.x > SCREEN_WIDTH:
            super().kill()

    @property
    def image(self):
        return self._img

    @property
    def rect(self):
        return self._rect

    @classmethod
    def init(cls):
        '''
        Initialize the picture for future Arrow objects. Since method calls 
        in here require pygame's image module to be initialized, this class
        method should not be called before pygame.init().
        '''
        cls.IMG = cls.IMG.convert()
        cls.IMG.set_colorkey(cls.IMG.get_at((0, 0)))


class DisplayGroup(pygame.sprite.Group):
    '''
    Class whose purpose is to draw every game object on the screen.
    '''

    def __init__(self, screen, background, *groups):
        '''
        Initialize a display group. groups are expected to be pygame.sprite.Group,
        or subclass.
        '''
        self._screen = screen
        self._background = background
        super().__init__()
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


class Target:
    pass

# for test purpose
if __name__ == '__main__':
    
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fps = 30
    background = pygame.image.load('resources/background.png')

    # Bow and Arrow init
    Bow.init()
    Arrow.init()
    # Bow instanciation
    bow = Bow()
    onscreen_sprites = DisplayGroup(screen,
                                    background,
                                    Bow.INSTANCES, Arrow.INSTANCES)

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
        pygame.display.flip()
        clock.tick(fps)
