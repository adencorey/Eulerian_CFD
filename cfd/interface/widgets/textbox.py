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
        self._text_offset = int(0.5 * (self.rect.height - self._font.get_height()))
        self.selected = False
        
    def get_input(self) -> str:
        return self.text if self.text else self.placeholder
        
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self._text_surf = self._font.render(self.text, True, self._main_clr)
        self._text_rect = self._text_surf.get_rect(topleft=(self.rect.topleft + self._text_offset * np.array((1, 1), dtype=np.uint8)))
        self._place_surf = self._font.render(self.placeholder, True, config.hvr_clr)
        self._place_rect = self._place_surf.get_rect(topleft=(self.rect.topleft + self._text_offset * np.array((1, 1), dtype=np.uint8)))
        
    def update(self, hvr_id, hl_id) -> None:
        self._update_text()
        
        
    #   ==========[ DRAW ]==========
    def _draw_text(self, screen) -> None:
        
        super()._draw_text(screen)
        if not self.selected and not self.text: screen.blit(self._place_surf, self._place_rect)
        
    def _draw_indicator(self, screen:pg.Surface) -> None:
        
        ind_surf = self._font.render("|", True, self._main_clr)
        ind_rect = ind_surf.get_rect(topleft=self._text_rect.topright)
        screen.blit(ind_surf, ind_rect)
    
    def draw(self, screen:pg.Surface) -> None:
        
        pg.draw.rect(screen, self._bg_clr, self.rect)
        pg.draw.rect(screen, self._main_clr, self.rect, self._border)
        super()._draw_text(screen)
        
        if self.selected:
            if pg.time.get_ticks() % 1000 < 500:
                self._draw_indicator(screen)
        else:
            if not self.text: screen.blit(self._place_surf, self._place_rect)