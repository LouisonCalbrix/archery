#! /usr/bin/env python3

# program: the super tiny bow game
# This is a mini game where you press the space bar to shoot an arrow at a target
# author: Louison Calbrix
# date: December 2019

import os
import pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

class Bow(pygame.sprite.Sprite):
    '''
    A bow moving across the screen from top to bottom and back.
    It can shoot arrows.
    '''
    IMG = pygame.image.load('resources/bow1.png')
    SPEED = [0, 5]

    def __init__(self):
        '''
        Create a Bow.
        '''
        super().__init__()
        self._img = Bow.IMG
        self._rect = self._img.get_rect()
        self._rect.move_ip(20, 0)
        self._speed = Bow.SPEED.copy()

    def update(self):
        '''
        Update bow's position, and whether or not an arrow is shot.
        '''
        self._rect.move_ip(*self._speed)
        if self._rect.y < 0 or self._rect.y > SCREEN_HEIGHT-self._rect.height:
            self._speed = [-speed_component for speed_component in self._speed]


class Arrow:
    pass

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
    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        bow.update()
        screen.blit(bow._img, bow._rect)
        pygame.display.flip()
        clock.tick(fps)
