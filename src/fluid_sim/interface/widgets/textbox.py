import pygame as pg

from enum import Enum

from fluid_sim.interface.config import Widget, config


class TextBox(Widget):
    
    def __init__(self, info:Enum, rect:pg.Rect, placeholder:str) -> None:
        super().__init__(info=info, rect=rect)
        
        self.placeholder = placeholder
        self.text_offset = int(0.5 * (self.rect.height - self.font.get_height()))
        
        
        self.selected = False
        
    
    def _update_text(self):
        
        if self.text: super()._update_text()
        self.place_surf = self.font.render(self.placeholder, True, config.hvr_clr)
        self.place_rect = self.place_surf.get_rect(left=(self.rect.left + self.text_offset))
        
    def update(self, hvr_id:int, hl_id:int) -> None:
        
        self._update_colours(hvr_id, hl_id)
        self._update_text()
        
        
    def draw(self, screen:pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        pg.draw.rect(screen, self.main_clr, self.rect, self.border)
        super()._draw_text(screen)
        
        if self.selected:
            pass
        else:
            if not self.text: screen.blit(self.place_surf, self.place_rect)
            
