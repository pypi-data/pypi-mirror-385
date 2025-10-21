import time
import pygamejr
import pygame

tank = pygamejr.ImageSprite(pygamejr.resources.image_tanks.tank_green)
tank.rect.centerx = pygamejr.screen.get_width() / 2
tank.rect.centery = pygamejr.screen.get_height() / 2


for frame in pygamejr.every_frame():
    pass
    # keys = pygame.key.get_pressed()
    #
    # if keys[pygame.K_SPACE]:
    #     fire(ship)
    #
    # if enemy.is_visible and is_hit_enemy(enemy):
    #     enemy.is_visible = False
    #
    # bullet_fly()