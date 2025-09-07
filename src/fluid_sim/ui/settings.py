import pygame as pg

import logging

logger = logging.getLogger(__name__)


class SettingsScreen:
    
    def __init__(self, width, height) -> None:
        
        self.screen_width = width
        self.screen_height = height
        
    def handle_events(self, event: pg.event) -> None:
        
        pass
    
    def update(self) -> None:
        
        pass
    
    def draw(self, screen: pg.Surface) -> None:
        
        pg.draw.circle(screen, (0, 0, 255), (self.screen_width // 2, self.screen_height // 2), 50)