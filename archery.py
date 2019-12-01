#! /usr/bin/env python3

# program: the super tiny bow game
# This is a mini game where you press the space bar to shoot an arrow at a target
# author: Louison Calbrix
# date: December 2019

import os
import pygame

class Bow(pygame.sprite.Sprite):
    '''
    A bow moving across the screen from top to bottom and back.
    It can shoot arrows.
    '''
    IMG = pygame.image.load('resources/bow.png')

    def __init__(self):
        '''
        Create a Bow.
        '''
        super().__init__()
        self._img = Bow.IMG

class Arrow:
    pass

class Target:
    pass
