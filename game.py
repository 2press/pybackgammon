import argparse
import math
import os
import random
import socket

import pygame
from PodSixNet.Connection import connection
from tools import scale_image


class Piece:
    def __init__(self, app, ident, pos=(0, 0), black=True):
        self.app = app
        self.dragging = False
        self.ident = ident
        self.black = black
        self.color = 'black' if self.black else 'white'
        self.image = scale_image(pygame.image.load(
            f"images/piece-{self.color}-2-sh.png"))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.offset = (0, 0)

    def update(self, screen):
        if self.dragging:
            pos = pygame.mouse.get_pos()
            self.rect.center = (pos[0] + self.offset[0],
                                pos[1] + self.offset[1])
            self.send_move()
        screen.blit(self.image, self.rect)

    def move(self, pos, screen):
        self.rect.center = (pos[0], pos[1])
        screen.blit(self.image, self.rect)

    def criclecolide(self, pos):
        if not self.rect.collidepoint(pos):
            return False

        d = math.sqrt(
            (self.rect.center[0] - pos[0])**2
            + (self.rect.center[1] - pos[1])**2
        )
        return d <= self.image.get_width()/2

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.criclecolide(event.pos):
            self.offset = (self.rect.center[0] - event.pos[0],
                           self.rect.center[1] - event.pos[1])
            self.dragging = True
            return True
        elif self.dragging and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            self.app.impact_sound.play()
            connection.Send({'action': 'impact'})
            return True
        elif self.dragging and event.type == pygame.MOUSEMOTION:
            return True
        else:
            return False

    def send_move(self):
        connection.Send({'action': 'move', 'piece': (
            self.ident, self.rect.center[0], self.rect.center[1])})


class Board:

    BG_COLOR = (255, 241, 221)
    WOOD_COLOR = (94, 72, 51)

    def __init__(self, app):
        self.app = app
        self.triangles = list()
        for row_idx in range(2):
            row = list()
            for color in ['dark', 'light']:
                image = pygame.image.load(
                    f"images/row{row_idx+1}-triangle-{color}.gif")
                row.append(image)
            self.triangles.append(row)
        self.black_arrow = scale_image(
            pygame.image.load("images/black_arrow.png"), 0.5)
        self.white_arrow = scale_image(
            pygame.image.load("images/white_arrow.png"), 0.5)
        self.triangle_width = self.triangles[0][0].get_width()
        self.triangle_height = self.triangles[0][0].get_height()

        self.distance_y = 100
        self.offset_y = (self.app.height -
                         self.distance_y) // 2 - self.triangle_height
        self.offset_x = self.app.width - 12*self.triangle_width

    def render(self, screen):
        screen.fill(self.BG_COLOR)

        for idx in range(12):
            screen.blit(self.triangles[0][idx % 2],
                        (idx*self.triangle_width + self.offset_x * (idx // 6), self.offset_y))
        wood = pygame.Rect(6*self.triangle_width, 0,
                           self.offset_x, screen.get_height())
        for idx in range(12):
            screen.blit(self.triangles[1][idx % 2],
                        (idx*self.triangle_width + self.offset_x * (idx // 6), self.triangle_height+self.offset_y+self.distance_y))

        pygame.draw.rect(screen, self.WOOD_COLOR, wood)

        online = self.app.player_count > 0
        text = f'{self.app.player_count} Spieler' if online else 'Offline'
        color = (255, 255, 255) if online else (255, 0, 0)
        text_surf = self.app.font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (self.app.width // 2, 15)
        screen.blit(text_surf, text_rect)

        rect = self.black_arrow.get_rect()
        rect.center = (20, self.app.height // 2 - 30)
        screen.blit(self.black_arrow, rect.center)
        rect = self.white_arrow.get_rect()
        rect.center = (20, self.app.height // 2 + 10)
        screen.blit(self.white_arrow, rect.center)


class Dice:

    def __init__(self, app):

        self.app = app
        self.roll_random()
        self.generate_fluctiatons()
        self.sound_effect = None
        self.cheer_sound = None
        self.images = [None]*2
        self.rects = [None]*2

    def roll(self, data=None):
        if self.sound_effect is None:
            self.sound_effect = pygame.mixer.Sound('sound/dice.wav')
        if self.cheer_sound is None:
            self.cheer_sound = pygame.mixer.Sound('sound/cheer.wav')
        if data is None:
            self.roll_random()
            self.generate_fluctiatons()
            self.send_state()
        else:
            self.generate_fluctiatons()
            self.dice = data['dice']
        if self.dice[0] == self.dice[1]:
            self.cheer_sound.play()
        self.sound_effect.play()

    def roll_random(self):
        self.dice = [random.randint(1, 6) for _ in range(2)]

    def generate_fluctiatons(self):
        self.rotation = random.sample(range(0, 360), 2)
        self.offset = random.sample(range(-10, 10), 4)

    def send_state(self):
        connection.Send({"action": "roll", 'dice': self.dice})

    def render(self, screen):
        for idx in range(2):
            self.images[idx] = pygame.image.load(
                f"images/digit-{self.dice[idx]}-white.png")
            self.images[idx] = pygame.transform.rotozoom(
                self.images[idx], self.rotation[idx], 1.0)
            x = self.app.width // 2 + \
                self.offset[2*idx]
            y = self.app.height // 2 + 40*(2*idx-1) + \
                self.offset[2*idx+1]
            self.rects[idx] = self.images[idx].get_rect()
            self.rects[idx].center = (x, y)
            screen.blit(self.images[idx], self.rects[idx])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for r in self.rects:
                if r.collidepoint(event.pos):
                    self.roll()
                    break


class OtherMouse:

    def __init__(self):
        self.visible = False
        self.pos = (0, 0)
        self.image = scale_image(pygame.image.load(f"images/crosshair.png"))
        self.rect = self.image.get_rect()

    def set_visible(self, visible=True):
        self.visible = visible

    def setPostion(self, pos):
        self.visible = True
        self.rect.center = self.pos = pos

    def render(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect)
