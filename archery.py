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

    IMG_UNBENT = pygame.image.load('resources/bow1.png')
    IMG_BENT = pygame.image.load('resources/bow2.png')
    SPEED = [0, 5]

    def __init__(self):
        '''
        Create a Bow.
        '''
        super().__init__()
        self._img = Bow.IMG_UNBENT
        self._rect = self._img.get_rect()
        self._rect.move_ip(20, 0)
        self._bent = False
        self._speed = Bow.SPEED.copy()
        self._arrow = Arrow

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
        self._img = Bow.IMG_UNBENT
        self._arrow(self._rect)


class Arrow(pygame.sprite.Sprite):
    '''
    An arrow that can be shot by a bow. It has an horizontal speed, that makes
    it move across the screen from left to right. It is destroyed if it goes
    beyond the screen's boundaries.
    '''
    IMG = pygame.image.load('resources/arrow.png')
    SPEED = [10, 0]
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
        self._rect.move_ip(self._speed)
        if self._rect.x > SCREEN_WIDTH:
            super().kill()

    def __del__(self):
        print('arrow deleted')

    @property
    def image(self):
        return self._img.copy()

    @property
    def rect(self):
        return self._rect.copy()

    @classmethod
    def init(cls):
        '''
        Initialize the picture for future Arrow objects. Since method calls 
        in here require pygame's image module to be initialized, this class
        method should not be called before pygame.init().
        '''
        cls.IMG.set_colorkey(cls.IMG.get_at((0, 0)))
        cls.IMG = cls.IMG.convert()

    @classmethod
    def draw(cls, screen):
        cls.INSTANCES.draw(screen)

    @classmethod
    def update_group(cls):
        cls.INSTANCES.update()

class Target:
    pass

# for test purpose
if __name__ == '__main__':
    
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fps = 40
    bow = Bow()
    Arrow.init()
    while True:
        screen.fill((0, 0, 0))
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
        bow.update()
        screen.blit(bow._img, bow._rect)
        Arrow.update_group()
        Arrow.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
