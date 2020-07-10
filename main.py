import pygame
import os
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'


def scale_image(image, scale=0.7):
    return pygame.transform.smoothscale(
        image, ((int)(image.get_width() * scale), (int)(image.get_height() * scale)))


class Piece:
    def __init__(self, pos=(0, 0), black=True):
        self.dragging = False
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
            return True
        elif self.dragging and event.type == pygame.MOUSEMOTION:
            return True
        else:
            return False


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
        self.offset_x = self.app.weight - 12*self.triangle_width

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


class App:
    def __init__(self):
        self._running = True
        self._screen = None
        self.size = self.weight, self.height = 1800, 960
        self.board = Board(self)
        self.init_pieces()

    def init_pieces(self):
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
        for field_id, field in enumerate(self.fields):
            top = field_id // 12 == 1
            for piece_id, is_black in enumerate(field):
                offset_x = self.board.triangle_width//2 + \
                    self.board.triangle_width * (field_id % 12) + \
                    ((field_id % 12) // 6) * self.board.offset_x
                x = offset_x if top else self.weight - offset_x
                ((field_id % 12) // 6) * self.board.offset_x
                y = self.piece_size * \
                    (piece_id*2+1) if top else self.height - \
                    self.piece_size * (piece_id*2+1)
                pos = (x, y)
                self.pieces.append(Piece(pos, is_black))

    def on_init(self):
        pygame.init()
        pygame.display.set_caption('Backgammon')
        self.clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
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

    def on_loop(self):
        pass

    def on_render(self):
        self.board.render(self._screen)
        for piece in self.pieces[::-1]:
            piece.update(self._screen)
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


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
