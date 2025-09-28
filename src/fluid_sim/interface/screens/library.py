import pygame as pg

import logging

from fluid_sim.interface.config import AppWidgets, config
from fluid_sim.interface.widgets import RectButton

logger = logging.getLogger(__name__)


class LibraryScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)
        
        self.btn_dim = (0.15 * config.width, 0.04 * config.height)
        
        # ==========[ CREATE PROJECT ]==========
        self.create_btn = RectButton(info=AppWidgets.CREATE_BTN, rect=pg.Rect(self._get_grid(0, 1), self.btn_dim), text="Create Project")
        
        self.hvr_name, self.hvr_id = None, None
        
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        """return suitable position for widgets in specific 'row and 'columns'"""
        
        if title:
            return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else:
            return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
        
        
    def handle_events(self, event: pg.event) -> None:
        
        pass
    
    def update(self) -> None:
        
        self.create_btn.update(self.hvr_id, None)
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, self.title_pos)
        
        #   draw buttons
        self.create_btn.draw(screen)