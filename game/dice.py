import random

import pygame
from PodSixNet.Connection import connection


class Dice:

    def __init__(self, app):
        self.app = app
        self.roll_random()
        self.generate_fluctuations()
        self.sound_effect = None
        self.cheer_sound = None
        self.images = [None]*2
        self.rects = [None]*2
        self.black = self.app.run_server
        self.reset()

    def reset(self):
        self.eye_counter = [0]*2

    def _load_sounds(self):
        if self.sound_effect is None:
            self.sound_effect = pygame.mixer.Sound('assets/sound/dice.wav')
        if self.cheer_sound is None:
            self.cheer_sound = pygame.mixer.Sound('assets/sound/cheer.wav')

    def roll(self, data=None):
        self._load_sounds()
        if data is None:
            self.roll_random()
            self.generate_fluctuations()
            self.black = self.app.run_server
            self.send_state()
        else:
            self.generate_fluctuations()
            self.dice = data['dice']
            self.black = not self.app.run_server

        eyes = sum(self.dice)

        if self.dice[0] == self.dice[1]:
            self.cheer_sound.play()
            eyes = 2*eyes
        self.eye_counter[0 if self.black else 1] += eyes
        self.sound_effect.play()

    def set_eye_counter(self, eyes):
        self.eye_counter = eyes

    def send_eyes(self):
        connection.Send({"action": "eyes", 'eyes': self.eye_counter})

    def roll_random(self):
        self.dice = [random.randint(1, 6) for _ in range(2)]

    def generate_fluctuations(self):
        self.rotation = random.sample(range(0, 360), 2)
        self.offset = random.sample(range(-10, 10), 4)

    def send_state(self):
        connection.Send({"action": "roll", 'dice': self.dice})

    def render(self, screen):
        color = 'black' if self.black else 'white'
        for idx in range(2):
            self.images[idx] = pygame.image.load(
                f"assets/images/digit-{self.dice[idx]}-{color}.png")
            self.images[idx] = pygame.transform.rotozoom(
                self.images[idx], self.rotation[idx], 1.0)
            x = self.app.width // 2 + \
                self.offset[2*idx]
            y = self.app.height // 2 + 40*(2*idx-1) + \
                self.offset[2*idx+1]
            self.rects[idx] = self.images[idx].get_rect()
            self.rects[idx].center = (x, y)
            screen.blit(self.images[idx], self.rects[idx])

    def _collides(self, pos) -> bool:
        for r in self.rects:
            if r is not None and r.collidepoint(pos):
                return True
        return False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._collides(event.pos):
            self.roll()
            return True
        if hasattr(event, 'pos') and self._collides(event.pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True
