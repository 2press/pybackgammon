import pygame


def scale_image(image, scale=0.7):
    return pygame.transform.smoothscale(
        image, (int(image.get_width() * scale), int(image.get_height() * scale)))
