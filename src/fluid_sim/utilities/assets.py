import pygame as pg

import os
import logging

logger = logging.getLogger(__name__)

ASSETS_PATH = os.path.relpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets"))

def load_image(filename: str) -> pg.Surface | None:
    
    filepath = os.path.join(ASSETS_PATH, "graphics", filename)
    if os.path.exists(filepath):
        logger.debug(f"Successfully fetched image from {filepath}")
        return pg.image.load(filepath).convert_alpha()
    
    else:
        logger.warning(f"Failed to fetch image, {filepath} does not exist")
        return
    
def recolour_image(surface: pg.Surface, old_colour, new_colour) -> pg.Surface:
    
    pixels = pg.PixelArray(surface)         #   convert image pixels into numpy array
    pixels.replace(old_colour, new_colour)  #   replace colours
    del pixels                              #   unlock array
    return surface