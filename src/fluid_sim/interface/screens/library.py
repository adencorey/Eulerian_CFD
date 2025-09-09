import pygame as pg

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import config

logger = logging.getLogger(__name__)


class LibraryScreen:
    
    def __init__(self) -> None:
        pass
        
    def handle_events(self, event: pg.event) -> None:
        
        pass
    
    def update(self) -> None:
        
        pass
    
    def draw(self, screen: pg.Surface) -> None:
        
        pg.draw.circle(screen, (255, 0, 0), (config.width // 2, config.height // 2), 50)