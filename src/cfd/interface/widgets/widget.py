import pygame as pg

from cfd.interface.config import registry, config

class Widget:
    
    def __init__(self, name:str, rect:pg.Rect, colours:tuple[tuple, tuple]=None, text:str=None, font:pg.font.Font=None) -> None:
        
        self.name, self.id = registry.register(name) if name else (None, None)
        self.rect = rect
        self.text = text
        self.font = font if font else config.font["body"]
        self.border = int(0.05 * self.rect.height)
        self.main_clr, self.bg_clr = colours if colours else config.main_clr, config.bg_clr
            
        
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return self.rect.collidepoint(mouse_pos)
    

    #   ==========[ UPDATE ]==========
    def _update_colours(self, hvr_id:int, hl_id:int) -> None:

        if self.id == hl_id:
            self.main_clr, self.bg_clr = config.secondary_clr, config.bg_clr
        elif self.id == hvr_id:
            self.main_clr, self.bg_clr = config.hl_clr, config.hvr_clr
        else:
            self.main_clr, self.bg_clr = config.main_clr, config.bg_clr
            
    def _update_text(self) -> None:
        
        self.text_surf = self.font.render(self.text, True, self.main_clr)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
    def update(self, hvr_id:int, hl_id:int) -> None:

        self._update_colours(hvr_id, hl_id)
        if self.text: self._update_text()
        
    
    #   ==========[ DRAW ]==========
    def _draw_text(self, screen:pg.Surface) -> None:
        if self.text: screen.blit(self.text_surf, self.text_rect)
    
    def draw(self, screen:pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        pg.draw.rect(screen, self.main_clr, self.rect, self.border)
        self._draw_text(screen)
    
class NullWidget:
    
    id = None
    name = None
NULLWIDGET = NullWidget()