# -*- coding: utf-8 -*-
import pgzrun
from pygame import Rect
import random
from typing import TYPE_CHECKING, Any
import pygame.mixer as mixer
import os
print("Çalışma dizini:", os.getcwd())
# TYPE_CHECKING ve modul tanimlamalari
if TYPE_CHECKING:
    from pgzero.screen import Screen
    from pgzero.keyboard import Keyboard
    from pgzero.music import _music
    from pgzero.soundfmt import sndfmt

    screen: Screen
    keyboard: Keyboard
    music: _music
    sndfmt: sndfmt
else:
    screen: Any
    keyboard: Any
    music: Any
    sndfmt: Any

# Pencere ayarlari
WIDTH = 800
HEIGHT = 600
TITLE = "Python Basic Platform"
GRAVITY = 0.8
JUMP_FORCE = -18

# Oyun durumlari
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Ozel Buton Sinifi
class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: tuple = (100, 200, 100),
                 hover_color: tuple = (150, 250, 150)):
        self.rect = Rect(x - width//2, y - height//2, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self):
        current_color = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, current_color)
        screen.draw.text(
            self.text,
            center=self.rect.center,
            fontsize=35,
            color=(255, 255, 255),
            shadow=(1, 1)
        )

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

class Hero:
    def __init__(self):
        self.rect = Rect(100, 480-80, 80, 110)
        self.animation_frame = 0
        self.animation_speed = 0.2

        # Animasyon kareleri
        self.idle_animation = ['player_idle', 'player_idle_flip2']
        self.walk_animation = ['player_walk1', 'player_walk2']
        self.jump_animation = ['player_jump']

        self.current_animation = self.idle_animation
        self.image = self.idle_animation[0]
        self.direction = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.lives = 3

    def update_animation(self):
        if not self.on_ground:
            self.current_animation = self.jump_animation
        elif self.velocity_x != 0:
            self.current_animation = self.walk_animation
        else:
            self.current_animation = self.idle_animation

        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.current_animation):
            self.animation_frame = 0

        # Karakterin yönüne göre doğru resmi seç
        base_image = self.current_animation[int(self.animation_frame)]
        self.image = base_image if self.direction == 1 else base_image + "_flip"

class Zombie:
    def __init__(self, x, y, patrol_range):
        self.rect = Rect(x, y, 80, 110)
        self.patrol_range = patrol_range
        self.direction = 1
        self.speed = 2
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.walk_frames = ['zombie_walk1', 'zombie_walk2']
        self.image = self.walk_frames[0]
        self.on_ground = False
        self.velocity_y = 0

    def patrol(self, platforms):
        self.rect.x += self.direction * self.speed

        # Zombi yerçekimi etkisi
        self.velocity_y += GRAVITY  # Yerçekimi
        self.rect.y += self.velocity_y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.velocity_y > 0:  # Zombi yere düşüyorsa
                    self.rect.bottom = plat.top  # Platforma otursun
                    self.velocity_y = 0  # Yerçekimini sıfırla
                    self.on_ground = True

        # Devriye alanı kontrolü
        if self.rect.x > self.patrol_range[1]:
            self.direction = -1
        elif self.rect.x < self.patrol_range[0]:
            self.direction = 1

        # Yürüme animasyonu
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.walk_frames):
            self.animation_frame = 0

        self.image = self.walk_frames[int(self.animation_frame)]
        if self.direction == -1:
            self.image += "_flip"

def create_world():
    global platforms, coins, enemies
    platforms = [
        Rect(0, HEIGHT - 40, WIDTH, 40),  # Ana zemin
        Rect(200, 480, 200, 20),  
        Rect(500, 380, 150, 20)   
    ]

    coins = [Rect(random.randint(100, WIDTH-100),
                 random.randint(100, HEIGHT-100), 16, 16) for _ in range(5)]
    
    # Zombileri güncellenmiş konumlarına yerleştiriyoruz
    enemies = [
        Zombie(300, 480 - 110, (250, 450)),  # 1. platform üstüne
        Zombie(550, 380 - 110, (500, 600)),  # 2. platform üstüne
        Zombie(150, 380 - 110, (100, 300)),  # 2. platformun solunda
        Zombie(650, HEIGHT - 40 - 110, (600, 750))  # Ana zemin üstüne
    ]

hero = Hero()
game_state = MENU
music_on = True

# Butonlar
start_btn = Button(WIDTH/2, 300, 200, 60, "Start Game")
music_btn = Button(WIDTH/2, 400, 200, 60, "Music: ON")
quit_btn = Button(WIDTH/2, 500, 200, 60, "Quit Game")

def load_valid_sound(path: str):
    """Desteklenen ses formatlarini yukle"""
    try:
        return mixer.Sound(path)
    except Exception as e:
        print(f"Ses yukleme hatasi: {str(e)}")
        exit()

# Sesler
try:
    jump_sound = load_valid_sound("sounds/jump.wav")
    coin_sound = load_valid_sound("sounds/coin.wav")
except Exception as e:
    print(f"Ses dosyasi hatasi: {str(e)}")
    exit()

def toggle_music():
    global music_on
    music_on = not music_on
    music_btn.text = f"Music: {'ON' if music_on else 'OFF'}"
    if music_on:
        music.play('bg_music')
    else:
        music.stop()
        jump_sound.set_volume(0)
        coin_sound.set_volume(0)

def start_game():
    global game_state
    create_world()
    hero.__init__()
    game_state = PLAYING
    if music_on:
        music.play('bg_music')
        jump_sound.set_volume(1)
        coin_sound.set_volume(1)

# Sesler
try:
    jump_sound = load_valid_sound("sounds/jump.wav")
    coin_sound = load_valid_sound("sounds/coin.wav")
    if not music_on:
        jump_sound.set_volume(0)
        coin_sound.set_volume(0)
except Exception as e:
    print(f"Ses dosyasi hatasi: {str(e)}")
    exit()

def on_mouse_move(pos):
    start_btn.check_hover(pos)
    music_btn.check_hover(pos)
    quit_btn.check_hover(pos)

def on_mouse_down(pos):
    global game_state
    if game_state == MENU:
        if start_btn.rect.collidepoint(pos):
            start_game()
        elif music_btn.rect.collidepoint(pos):
            toggle_music()
        elif quit_btn.rect.collidepoint(pos):
            exit()

def update():
    global game_state

    if game_state == PLAYING:
        hero.velocity_x = 0
        if keyboard.left:
            hero.velocity_x = -5
            hero.direction = -1
        if keyboard.right:
            hero.velocity_x = 5
            hero.direction = 1
        if keyboard.space and hero.on_ground:
            hero.velocity_y = JUMP_FORCE
            jump_sound.play()

        hero.velocity_y += GRAVITY
        hero.rect.y += hero.velocity_y
        hero.rect.x += hero.velocity_x

        hero.on_ground = False
        for plat in platforms:
            if hero.rect.colliderect(plat):
                if hero.velocity_y > 0:  # Sadece düşerken etkilesin
                    hero.rect.bottom = plat.top
                    hero.velocity_y = 0
                    hero.on_ground = True

        for enemy in enemies:
            enemy.patrol(platforms)
            if enemy.rect.colliderect(hero.rect):
                hero.lives -= 1
                if hero.lives <= 0:
                    game_state = GAME_OVER
                hero.rect.x, hero.rect.y = 100, 400

        global coins
        for coin in coins[:]:
            if hero.rect.colliderect(coin):
                coins.remove(coin)
                coin_sound.play()
        if not coins:
            game_state = GAME_OVER

def draw():
    screen.clear()

    if game_state == MENU:
        screen.draw.text("Main Menu", center=(WIDTH/2, 100),
                        fontsize=60, color=(255, 255, 255))
        start_btn.draw()
        music_btn.draw()
        quit_btn.draw()

    elif game_state == PLAYING:
        for plat in platforms:
            screen.draw.filled_rect(plat, (100, 200, 100))
        for coin in coins:
            screen.draw.filled_rect(coin, (255, 215, 0))

        hero.update_animation()
        screen.blit(hero.image, (hero.rect.x, hero.rect.y))
        for enemy in enemies:
            screen.blit(enemy.image, (enemy.rect.x, enemy.rect.y))

        screen.draw.text(f"Lives: {hero.lives}", (10, 10),
                        fontsize=40, color=(255, 255, 255))
        screen.draw.text(f"Coins: {5-len(coins)}/5",
                        (WIDTH-150, 10), fontsize=40,
                        color=(255, 255, 255))
    else:
        text = "Game Over" if hero.lives <= 0 else "You Win!"
        screen.draw.text(text, center=(WIDTH/2, HEIGHT/2),
                        fontsize=100, color=(255, 50, 50))

pgzrun.go()