from utilities import scale_image
import pygame


class OtherMouse:

    def __init__(self):
        self.visible = False
        self.pos = (0, 0)
        self.image = scale_image(pygame.image.load(
            f"assets/images/crosshair.png"))
        self.rect = self.image.get_rect()

    def set_visible(self, visible=True):
        self.visible = visible

    def setPostion(self, pos):
        self.visible = True
        self.rect.center = self.pos = pos

    def render(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect)
