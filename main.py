import os
import random
import sys
import threading

import pygame

from boss import Boss
from enemy import Enemy
from laser import collide
from player import Player

pygame.font.init()

WIDTH, HEIGHT = 750, 750
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load images
ENEMY_SHIP = pygame.image.load(os.path.join("assets", "enemy.png"))

# Player
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "player.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
run = True
lost = False
enemies = []
lives = 10

player = Player(300, 630)

main_font = pygame.font.SysFont("comicsans", 30)
lost_font = pygame.font.SysFont("comicsans", 40)
title_font = pygame.font.SysFont("comicsans", 50)


def player_move(player, player_vel):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x - player_vel > 0:  # left
        player.x -= player_vel
    if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
        player.x += player_vel
    if keys[pygame.K_w] and player.y - player_vel > 0:  # up
        player.y -= player_vel
    if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
        player.y += player_vel
    if keys[pygame.K_SPACE]:
        player.shoot()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()


def main():
    global run, enemies
    FPS = 60
    level = 0

    enemies = []
    enemy_vel_max = 3
    enemy_vel_min = 1

    # bosses with their own layers
    bosses = []
    layers = []

    bosses_count = 2
    wave_length = 3
    for i in range(wave_length):
        enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-150, -30))
        enemy_vel = random.randrange(enemy_vel_min, enemy_vel_max)
        enemy1.vel = enemy_vel
        enemies.append(enemy1)

    player_vel = 5

    clock = pygame.time.Clock()
    mutex = threading.Lock()

    def redraw_window():
        SCREEN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        hp_label = main_font.render(f"Health: {player.health}", 1, (255, 255, 255))
        enemies_label = main_font.render(f"Enemies: {len(enemies)}", 1, (255, 255, 255))
        bosses_label = main_font.render(f"Bosses: {len(bosses)}", 1, (255, 255, 255))

        SCREEN.blit(lives_label, (10, 10))
        SCREEN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        SCREEN.blit(hp_label, (10, HEIGHT - 50))
        SCREEN.blit(enemies_label, (WIDTH - 170, HEIGHT - 50))
        SCREEN.blit(bosses_label, (WIDTH - 330, HEIGHT - 50))
        for enemy1 in enemies:
            enemy1.draw(SCREEN)
        player.draw(SCREEN)

        # blitting bosses' layers onto the main window
        for layer in layers:
            SCREEN.blit(layer, (0, 0))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        global lost

        if player.health <= 0:
            lost = True
            run = False

        if len(enemies) == 0 and len(bosses) == 0:
            level += 1
            wave_length += 3
            if level % 2 == 0:
                bosses_count += 1

            for i in range(wave_length):
                enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-150, -30))
                enemy_vel = random.randrange(enemy_vel_min, enemy_vel_max)
                enemy1.vel = enemy_vel
                enemies.append(enemy1)

            # creating bosses and their layers
            for i in range(bosses_count):
                # transparent layers on which bosses are going to be shown
                layer = pygame.Surface((WIDTH, HEIGHT))
                layer.set_colorkey((255, 255, 0))
                layers.append(layer)

                # creating a boss, assigning it its layer and starting its thread
                boss = Boss(random.randrange(100, WIDTH - 200), random.randrange(0, HEIGHT - 300), layer)

                bosses.append(boss)
                boss.start()

        # if boss' health is 0 or less - removing boss
        for boss in bosses:
            if boss.health <= 0:
                index = bosses.index(boss)
                boss.join()
                bosses.remove(boss)
                layers.remove(layers[index])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                for boss in bosses:
                    mutex.acquire()
                    try:
                        boss.health = 0
                        boss.join()
                    finally:
                        mutex.release()
                quit()

        player_move(player, player_vel)
        player.move_lasers(-5, enemies, bosses)
        # checking for collision between player and enemies
        for enemy in enemies:
            enemy.enemy_interaction(player, enemies, lives)

        # checking for collision between player and bosses
        for boss in bosses:
            mutex.acquire()
            try:
                if collide(boss, player):
                    player.health -= 5
            finally:
                mutex.release()


def main_menu():
    run_game = True
    while run_game:
        SCREEN.blit(BG, (0, 0))
        if lost:
            lost_label = lost_font.render("You Lost!! Press the mouse to exit", 1, (255, 255, 255))
            SCREEN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    run_game = False
        else:
            title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
            SCREEN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    main()

    pygame.quit()


main_menu()
