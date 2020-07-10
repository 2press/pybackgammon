import argparse
import math
import os
import random
import socket
import time
from weakref import WeakKeyDictionary

import pygame
import requests
from PodSixNet.Channel import Channel
from PodSixNet.Connection import ConnectionListener, connection
from PodSixNet.Server import Server

os.environ['SDL_VIDEO_CENTERED'] = '1'


class ClientChannel(Channel):

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Network_resetboard(self, data):
        self._server.sendToOthers(data, self)

    def Network_roll(self, data):
        self._server.sendToOthers(data, self)

    def Network_move(self, data):
        self._server.sendToOthers(data, self)

    def Network_impact(self, data):
        self._server.sendToOthers(data, self)

    def Close(self):
        self._server.delPlayer(self)


class MyServer(Server):

    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        ip = get_my_ip()
        port = kwargs['localaddr'][1]
        print(f'Starting Server on {ip}:{port}')

    def Connected(self, channel, addr):
        self.addPlayer(channel)
        self.sendPlayers()

    def addPlayer(self, player):
        print("New Player" + str(player.addr))
        self.players[player] = True
        print("players", [p for p in self.players])

    def delPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.sendPlayers()

    def sendPlayers(self):
        for p in self.players:
            p.Send({'action': 'playercount', 'count': len(self.players)})

    def sendToOthers(self, data, channel):
        for player in self.players:
            if player != channel:
                player.Send(data)


def scale_image(image, scale=0.7):
    return pygame.transform.smoothscale(
        image, ((int)(image.get_width() * scale), (int)(image.get_height() * scale)))


def get_my_ip():
    url = 'https://api.ipify.org'
    return requests.get(url=url).text


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

        text = self.app.font.render(
            f'{self.app.player_count} Spieler', True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.app.width // 2, 15)
        screen.blit(text, text_rect)


class Dieces:

    def __init__(self, app):

        self.app = app
        self.dieces = random.sample(range(1, 7), 2)
        self.rotation = random.sample(range(0, 360), 2)
        self.offset = random.sample(range(-10, 10), 4)
        self.sound_effect = None
        self.images = [None]*2
        self.rects = [None]*2

    def roll(self, data=None):
        if self.sound_effect is None:
            self.sound_effect = pygame.mixer.Sound('sound/dices.wav')
        if data is None:
            self.dieces = random.sample(range(1, 7), 2)
            self.rotation = random.sample(range(0, 360), 2)
            self.offset = random.sample(range(-10, 10), 4)
            connection.Send({"action": "roll", 'dieces': self.dieces})
        else:
            self.rotation = random.sample(range(0, 360), 2)
            self.offset = random.sample(range(-10, 10), 4)
            self.dieces = data['dieces']
        self.sound_effect.play()

    def render(self, screen):
        for idx in range(2):
            self.images[idx] = pygame.image.load(
                f"images/digit-{self.dieces[idx]}-white.png")
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


class App(ConnectionListener):
    def __init__(self, host, port, run_server=False):
        self._running = True
        self._screen = None
        self.reset_sound = None
        self.size = self.width, self.height = 1800, 960
        self.board = Board(self)
        self.init_pieces()
        self.dieces = Dieces(self)
        self.run_server = run_server
        self.player_count = 0
        port = int(port)
        if self.run_server:
            self.server = MyServer(localaddr=(host, port))
        self.Connect((host, port))

    def init_pieces(self, send=True):
        self.pieces = list()
        self.fields = [[] for _ in range(24)]
        self.fields[0] = [True] * 2
        self.fields[5] = [False] * 5
        self.fields[7] = [False] * 3
        self.fields[11] = [True] * 5
        self.fields[23] = [False] * 2
        self.fields[18] = [True] * 5
        self.fields[16] = [True] * 3
        self.fields[12] = [False] * 5
        self.pieces = list()
        self.piece_size = 42
        ident = 1
        for field_id, field in enumerate(self.fields):
            top = field_id // 12 == 1
            for piece_id, is_black in enumerate(field):
                offset_x = self.board.triangle_width//2 + \
                    self.board.triangle_width * (field_id % 12) + \
                    ((field_id % 12) // 6) * self.board.offset_x
                x = offset_x if top else self.width - offset_x
                ((field_id % 12) // 6) * self.board.offset_x
                y = self.piece_size * \
                    (piece_id*2+1) if top else self.height - \
                    self.piece_size * (piece_id*2+1)
                pos = (x, y)
                self.pieces.append(Piece(self, ident, pos, is_black))
                ident += 1

        if self.reset_sound is not None:
            self.reset_sound.play()
            if send:
                connection.Send({"action": "resetboard"})

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        self.reset_sound = pygame.mixer.Sound('sound/button.wav')
        self.impact_sound = pygame.mixer.Sound('sound/impact.wav')
        self.font = pygame.font.Font(pygame.font.get_default_font(), 22)
        pygame.display.set_caption('Backgammon')
        self.clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.dieces.roll()
            elif event.key == pygame.K_ESCAPE:
                self.init_pieces()
        else:
            for idx, piece in enumerate(self.pieces):
                if piece.handle_event(event):
                    if idx == 0:
                        break
                    for idx2, piece2 in enumerate(self.pieces):
                        if idx == idx2:
                            continue
                        if piece.rect.colliderect(piece2.rect):
                            break
                    else:
                        self.pieces.insert(0, self.pieces.pop(idx))
                    break
            else:
                self.dieces.handle_event(event)

    def on_loop(self):
        connection.Pump()
        self.Pump()
        if self.run_server:
            self.server.Pump()

    def on_render(self):
        self.board.render(self._screen)
        for piece in self.pieces[::-1]:
            piece.update(self._screen)
        self.dieces.render(self._screen)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            self.clock.tick(60)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def Network_connected(self, data):
        print("Connected to the Server")

    def Network_resetboard(self, data):
        self.init_pieces(False)

    def Network_roll(self, data):
        self.dieces.roll(data)

    def Network_impact(self, data):
        self.impact_sound.play()

    def Network_playercount(self, data):
        self.player_count = int(data['count'])

    def Network_move(self, data):
        piece_move = data['piece']
        for piece in self.pieces:
            if piece.ident == piece_move[0]:
                piece.move((piece_move[1], piece_move[2]), self._screen)
                break
        else:
            raise ValueError('Invalid piece ident!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Backgammon")
    parser.add_argument("--server", action="store_true")
    parser.add_argument(
        "--host", default=socket.gethostbyname(socket.gethostname()))
    parser.add_argument("--port", default='61096')
    args = parser.parse_args()
    theApp = App(args.host, args.port, args.server)
    theApp.on_execute()
