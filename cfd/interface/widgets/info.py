import pygame as pg
import numpy as np

from cfd.interface.config import config
from cfd.interface.widgets import Widget

class Info(Widget):
    
    def __init__(self, name:str, title:str, pos:tuple, description:str=None, line_max:int=45, font=config.font["body"], desc_font=config.font["sub"]) -> None:
        super().__init__(name=name, rect=pg.Rect(pos, (0, 0)), font=font)
        
        self.title = title
        self.line_max = line_max
        self.description = self.break_description(description) if description else None
        
        self.pos = self.rect.topleft
        self.desc_font = desc_font
        self.radius = 0.4 * self.font.get_height()
        self.padding = self.border * np.array((10, 5))
        self.update()
        
    
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return (self.btn_center[0] - mouse_pos[0]) ** 2 + (self.btn_center[1] - mouse_pos[1]) ** 2 <= self.radius ** 2 if self.description else False
    
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
        placeholder = self.description[0] if num_lines == 1 else self.line_max * "'/"
        w, h = self.desc_font.size(placeholder)
        h *= num_lines
        w, h = self.padding + np.array((w, h))
        
        #   determine anchor
        px -= w
        py -= h
        if px - w < 0: px += w
        if py - h < 0: py += h
        return px, py, w, h
        
    #   ==========[ UPDATE ]==========
    def _update_colours(self) -> None:
        self.main_clr, self.bg_clr = config.main_clr, config.bg_clr
            
    def _update_text(self) -> None:
        
        self.title_surf = self.font.render(self.title, True, self.main_clr)
        self.title_rect = self.title_surf.get_rect(left=self.rect.left + 3 * self.radius, centery=self.rect.centery)
        self.btn_center = (self.rect.left + 1.5 * self.radius, self.title_rect.centery)
        
        if self.description:
            self.desc_rect = pg.Rect(self.get_desc_pos())
            self.symbol_surf = self.desc_font.render("?", True, self.main_clr)
            self.symbol_rect = self.symbol_surf.get_rect(center=self.btn_center)

    def update(self, *args, **kwargs) -> None:
        self._update_colours()
        self._update_text()
        
    
    #   ==========[ DRAW ]==========   
    def _draw_text(self, screen:pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_rect)
        if self.description: screen.blit(self.symbol_surf, self.symbol_rect)
            
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
        
        if self.description:
            pg.draw.circle(screen, self.bg_clr, self.btn_center, self.radius)
            pg.draw.circle(screen, self.main_clr, self.btn_center, self.radius, int(0.07 * self.desc_font.get_height()))
        self._draw_text(screen)