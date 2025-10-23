import pygame as pg
import numpy as np

from cfd.interface.config import config
from .widget import Widget


class TextBox(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, placeholder:str, max:int, anchor:str=None) -> None:
        super().__init__(name=name, rect=rect, anchor=anchor, font=config.font["head"])
        
        self.text = ""
        self.max = max
        self.placeholder = placeholder
        self.text_offset = int(0.5 * (self.rect.height - self.font.get_height()))
        
        self.selected = False
        
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self.text_surf = self.font.render(self.text, True, self.main_clr)
        self.text_rect = self.text_surf.get_rect(topleft=(self.rect.topleft + self.text_offset * np.array((1, 1), dtype=np.uint8)))
        self.place_surf = self.font.render(self.placeholder, True, config.hvr_clr)
        self.place_rect = self.place_surf.get_rect(topleft=(self.rect.topleft + self.text_offset * np.array((1, 1), dtype=np.uint8)))
        
    def update(self, hvr_id, hl_id) -> None:
        self._update_text()
        
        
    #   ==========[ DRAW ]==========
    def _draw_text(self, screen) -> None:
        
        super()._draw_text(screen)
        if not self.selected and not self.text: screen.blit(self.place_surf, self.place_rect)
        
    def _draw_indicator(self, screen:pg.Surface) -> None:
        
        ind_surf = self.font.render("|", True, self.main_clr)
        ind_rect = ind_surf.get_rect(topleft=self.text_rect.topright)
        screen.blit(ind_surf, ind_rect)
    
    def draw(self, screen:pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        pg.draw.rect(screen, self.main_clr, self.rect, self.border)
        super()._draw_text(screen)
        
        if self.selected:
            if pg.time.get_ticks() % 1000 < 500:
                self._draw_indicator(screen)
        else:
            if not self.text: screen.blit(self.place_surf, self.place_rect)
            
