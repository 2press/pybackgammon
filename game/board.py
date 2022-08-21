import pygame
from utilities import scale_image


class Board:

    BG_COLOR = (255, 241, 221)
    WOOD_COLOR = (94, 72, 51)

    def __init__(self, app):
        self.app = app
        self._generate_board()

    def _generate_board(self):
        self.triangles = list()
        self.bounding_box_width = 80
        self.height = self.app.height - 2*self.bounding_box_width
        self.width = self.app.width - 2*self.bounding_box_width
        for row_idx in range(2):
            self.triangles.append([pygame.image.load(
                f"assets/images/row{row_idx+1}-triangle-{color}.gif") for color in ['dark', 'light']])
        self.black_arrow = scale_image(
            pygame.image.load("assets/images/black_arrow.png"), 0.5)
        self.white_arrow = scale_image(
            pygame.image.load("assets/images/white_arrow.png"), 0.5)
        self.v_line = pygame.image.load("assets/images/v-line.gif")
        self.triangle_width = self.triangles[0][0].get_width()
        self.triangle_height = self.triangles[0][0].get_height()

        self.distance_y = 100
        self.offset_y = (self.height -
                         self.distance_y) // 2 - self.triangle_height
        self.offset_x = self.width - 12*self.triangle_width

    def render_board(self, screen):
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.BG_COLOR)
        for idx in range(12):
            x = idx*self.triangle_width + self.offset_x * (idx // 6)
            self.surface.blit(self.triangles[0][idx % 2],
                              (x, self.offset_y))
            self.surface.blit(self.triangles[1][idx % 2],
                              (x, self.triangle_height+self.offset_y+self.distance_y))

        wood = pygame.Rect(6*self.triangle_width, 0,
                           self.offset_x, self.height)

        pygame.draw.rect(self.surface, self.WOOD_COLOR, wood)

        rect = self.black_arrow.get_rect()
        rect.center = (20, self.height // 2 - 30)
        self.surface.blit(self.black_arrow, rect.center)

        rect = self.white_arrow.get_rect()
        rect.center = (20, self.height // 2 + 10)
        self.surface.blit(self.white_arrow, rect.center)

        for idx, counter in enumerate(self.app.dice.eye_counter):
            color = (255, 255, 255) if idx == 1 else (0, 0, 0)
            text_surf = self.app.font.render(f'{counter}', True, color)
            text_rect = text_surf.get_rect()
            text_rect.center = (self.width // 2 + 35 *
                                (2*idx-1), self.height - 20)
            self.surface.blit(text_surf, text_rect)

        screen.blit(self.surface, (self.bounding_box_width,
                                   self.bounding_box_width))

    def render(self, screen):
        screen.fill(self.WOOD_COLOR)
        self.render_board(screen)

        screen.blit(self.v_line, (self.app.width // 2, 0))

        online = self.app.player_count > 0
        color = (255, 255, 255) if online else (255, 0, 0)
        text_surf = self.app.font.render(self._get_text(), True, color)
        text_rect = text_surf.get_rect()
        text_rect.center = (self.app.width // 2, 15)
        screen.blit(text_surf, text_rect)

    def _get_text(self) -> str:
        if not self.app.player_count:
            return 'Offline'
        if self.app.player_count == 1:
            return 'Online'
        return f'{self.app.player_count} Players'
