import pygame
from ..base import screen

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 500
HEIGHT = 500

sprites = []

class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, *args):
        super().__init__(*args)
        self.is_visible = True
        sprites.append(self)

    def __del__(self):
        sprites.remove(self)

    def draw(self):
        if self.is_visible:
            screen.blit(self.image, self.rect)
