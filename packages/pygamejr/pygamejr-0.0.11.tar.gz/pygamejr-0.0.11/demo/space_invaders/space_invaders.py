import pygamejr
import pygame
import bullets

# корабль
ship = pygamejr.ImageSprite('../assets/Ship.png')
ship.rect.bottom = pygamejr.screen.get_height() - 50

# враги
enemies = []
for top in range(50, 300, 50):
   for left in range(100, pygamejr.screen.get_width() - 100, 50):
       enemy = pygamejr.ImageSprite("../assets/InvaderA_00.png")
       enemy.rect.top = top
       enemy.rect.left = left
       enemies.append(enemy)

vertical_speed = 1

def move_vertically():
    '''Движение врагов по вертикали'''
    for enemy in enemies:
        enemy.rect.centery += vertical_speed
        if enemy.rect.centery >= pygamejr.screen.get_height()-200:
            print('game over')

horizontal_speed = 1
horizontal_limit = 0

def move_horizontally():
   '''Движение врагов по горизонтали'''
   global horizontal_speed
   global horizontal_limit
   for enemy in enemies:
       enemy.rect.centerx += horizontal_speed

   horizontal_limit += horizontal_speed
   if horizontal_limit > 50 or horizontal_limit == 0:
       horizontal_speed *= -1

def is_hit_enemy_by_bullet():
   '''проверяет попали ли пуля во врага'''
   for enemy in enemies:
       if bullets.is_hit_enemy(enemy):
           enemy.is_visible = False
           enemies.remove(enemy)
           return True
   return False

for frame in pygamejr.every_frame():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        bullets.fire(ship)

    if keys[pygame.K_d] and ship.rect.right <= pygamejr.screen.get_width():
        ship.rect.centerx += 3

    if keys[pygame.K_a] and ship.rect.left >= 0:
        ship.rect.centerx -= 3

    is_hit_enemy_by_bullet()

    bullets.fly()

    move_vertically()
    move_horizontally()
