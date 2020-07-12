import pygame
from PodSixNet.Connection import ConnectionListener, connection

from game import Board, Dice, Piece, OtherMouse
from server import BackgammonServer


class App(ConnectionListener):
    def __init__(self, host, port, run_server=False):
        self._running = True
        self._screen = None
        self.reset_sound = None
        self.run_server = run_server
        self.size = self.width, self.height = 1800, 960
        self.board = Board(self)
        self.dice = Dice(self)
        self.init_pieces()
        self.player_count = 0
        self.other_mouse = OtherMouse()
        if self.run_server:
            self.server = BackgammonServer(localaddr=(host, port))
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
        self.ping_iter = 0
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
        self.dice.reset()

        if self.reset_sound is not None:
            self.reset_sound.play()
            if send:
                connection.Send({"action": "resetboard"})

    def send_gamestate(self):
        pieces = list()
        for p in self.pieces:
            p.send_move()
        self.dice.send_state()
        self.dice.send_eyes()

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

    def ping(self):
        connection.Send({"action": "ping"})

    def keep_connection_alive(self):
        # Ping every 4 seconds
        self.ping_iter = (self.ping_iter + 1) % 240
        if self.ping_iter == 0:
            self.ping()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.dice.roll()
            elif event.key == pygame.K_ESCAPE:
                self.init_pieces()
        else:
            self.handle_piece_events(event)
            if event.type == pygame.MOUSEMOTION:
                connection.Send({'action': 'mousemotion', 'pos': event.pos})

    def handle_piece_events(self, event):
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
            self.dice.handle_event(event)

    def on_loop(self):
        self.keep_connection_alive()
        connection.Pump()
        self.Pump()
        if self.run_server:
            self.server.Pump()

    def on_render(self):
        self.board.render(self._screen)
        for piece in self.pieces[::-1]:
            piece.update(self._screen)
        self.dice.render(self._screen)
        self.other_mouse.render(self._screen)
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
        print("Connected to the server")

    def Network_disconnected(self, data):
        print("Disconnected from the server")
        self.player_count = 0

    def Network_resetboard(self, data):
        self.init_pieces(False)

    def Network_roll(self, data):
        self.dice.roll(data)

    def Network_impact(self, data):
        self.impact_sound.play()

    def Network_eyes(self, data):
        self.dice.set_eye_counter(data['eyes'])

    def Network_pong(self, data):
        pass

    def Network_mousemotion(self, data):
        self.other_mouse.setPostion(data['pos'])

    def Network_playercount(self, data):
        new_player_count = int(data['count'])
        if self.run_server and new_player_count > self.player_count:
            self.send_gamestate()
        self.player_count = new_player_count
        if self.player_count < 2:
            self.other_mouse.set_visible(False)

    def Network_move(self, data):
        piece_move = data['piece']
        for piece in self.pieces:
            if piece.ident == piece_move[0]:
                piece.move((piece_move[1], piece_move[2]), self._screen)
                break
        else:
            raise ValueError('Invalid piece ident!')
