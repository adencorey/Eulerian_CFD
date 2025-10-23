import pygame as pg
import numpy as np

from cfd.interface.config import config
from cfd.interface.widgets import Widget

class WidgetInfo(Widget):
    
    def __init__(self, name:str, title:str, pos:tuple, description:str, line_max:int=45) -> None:
        super().__init__(name=name, rect=pg.Rect(pos, (0, 0)), font=config.font["head"])
        
        self.title = title
        self.line_max = line_max
        self.description = self.break_description(description)
        
        self.pos = self.rect.topleft
        self.desc_font = config.font["sub"]
        self.radius = 0.43 * self.font.get_height()
        self.padding = self.border * np.array((10, 5))
        self.update()
        
    
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return (self.btn_center[0] - mouse_pos[0]) ** 2 + (self.btn_center[1] - mouse_pos[1]) ** 2 <= self.radius ** 2
    
    def break_description(self, description:str) -> list[str]:
        """splits description into multiple lines if needed"""
        
        #   word length check
        words = description.split()
        for word in words:
            if len(word) > self.line_max:
                raise ValueError(f"All words must be within {self.line_max} letters ({word})")
        
        break_idx = []
        i = self.line_max - 1
        while True:
            if i > len(description) - 1: break      #   break when reaches end of description
            while description[i] != " ": i -= 1     #   snap index to nearest whitespace at line break
            break_idx.append(i)
            i += self.line_max
        lst = list(description)
        for idx in break_idx:
            lst[idx] = "\n"
        return "".join(lst).splitlines()
        
    
    def get_desc_pos(self) -> tuple[int, int]:
        """returns a suitable position for description box that avoids overflowing texts outside screen border"""
        
        px, py = self.btn_center
        num_lines = len(self.description)
        
        #   get dimension of description box
        if num_lines == 1:
            w, h = self.padding + self.desc_font.size(self.description[0])
        else:
            w, h = self.padding + self.desc_font.size(self.line_max * "'/")
        h *= num_lines
        
        #   determine anchor
        if px + w > config.width: px -= w
        if py + h > config.height: py -= h
        return px, py, w, h
        
    #   ==========[ UPDATE ]==========
    def _update_colours(self) -> None:
        self.main_clr, self.bg_clr = config.main_clr, config.bg_clr
            
    def _update_text(self) -> None:
        
        self.title_surf = self.font.render(self.title, True, self.main_clr)
        self.title_rect = self.title_surf.get_rect(topleft=self.pos)
        self.btn_center = self.title_rect.right + 2 * self.radius, self.title_rect.centery
        self.desc_rect = pg.Rect(self.get_desc_pos())
        
        self.symbol_surf = self.desc_font.render("?", True, self.main_clr)
        self.symbol_rect = self.symbol_surf.get_rect(center=self.btn_center)

    def update(self, *args, **kwargs) -> None:
        self._update_colours()
        self._update_text()
        
    
    #   ==========[ DRAW ]==========   
    def _draw_text(self, screen:pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_rect)
        screen.blit(self.symbol_surf, self.symbol_rect)
            
    def draw_description(self, screen:pg.Surface) -> None:
        
        #   draw background
        pg.draw.rect(screen, self.bg_clr, self.desc_rect)
        pg.draw.rect(screen, self.main_clr, self.desc_rect, self.border)
        
        #   draw texts
        topleft = self.desc_rect.topleft + 0.5 * self.padding
        for i, line in enumerate(self.description):
            surf = self.desc_font.render(line, True, self.main_clr)
            pos = topleft + self.desc_font.get_height() * i * np.array((0, 1))
            rect = surf.get_rect(topleft=pos)
            screen.blit(surf, rect)
    
    def draw(self, screen:pg.Surface) -> None:
        
        pg.draw.circle(screen, self.bg_clr, self.btn_center, self.radius)
        pg.draw.circle(screen, self.main_clr, self.btn_center, self.radius, int(0.1 * self.desc_font.get_height()))
        self._draw_text(screen)