import math

import pygame
from PodSixNet.Connection import connection
from utilities import scale_image


class Piece:
    def __init__(self, app, ident, pos=(0, 0), black=True):
        self.app = app
        self.dragging = False
        self.ident = ident
        self.black = black
        self.color = 'black' if self.black else 'white'
        self.image = scale_image(pygame.image.load(
            f"assets/images/piece-{self.color}-2-sh.png"))
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
