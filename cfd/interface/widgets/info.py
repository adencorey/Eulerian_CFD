import pygame as pg
import numpy as np

from cfd.interface.config import config
from cfd.interface.widgets import Widget

class Info(Widget):
    
    def __init__(self, name:str, title:str, pos:tuple, description:str=None, line_max:int=45, font=config.font["body"], desc_font=config.font["sub"]) -> None:
        super().__init__(name=name, rect=pg.Rect(pos, (0, 0)), font=font)
        
        self.title = title
        self._line_max = line_max
        self._description = self.break_description(description) if description else None
        
        self.pos = self.rect.topleft
        self._desc_font = desc_font
        self._radius = 0.4 * self._font.get_height()
        self._padding = self._border * np.array((10, 5))
        self.update()
        
    
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return (self.btn_center[0] - mouse_pos[0]) ** 2 + (self.btn_center[1] - mouse_pos[1]) ** 2 <= self._radius ** 2 if self._description else False
    
    def break_description(self, description:str) -> list[str]:
        """splits description into multiple lines if needed"""
        
        #   word length check
        words = description.split()
        for word in words:
            if len(word) > self._line_max:
                raise ValueError(f"All words must be within {self._line_max} letters ({word})")
        
        break_idx = []
        i = self._line_max - 1
        while True:
            if i > len(description) - 1: break      #   break when reaches end of description
            while description[i] != " ": i -= 1     #   snap index to nearest whitespace at line break
            break_idx.append(i)
            i += self._line_max
        lst = list(description)
        for idx in break_idx:
            lst[idx] = "\n"
        return "".join(lst).splitlines()
        
    
    def get_desc_pos(self) -> tuple[int, int]:
        """returns a suitable position for description box that avoids overflowing texts outside screen border"""
        
        px, py = self.btn_center
        num_lines = len(self._description)
        
        #   get dimension of description box
        placeholder = self._description[0] if num_lines == 1 else self._line_max * "'/"
        w, h = self._desc_font.size(placeholder)
        h *= num_lines
        w, h = self._padding + np.array((w, h))
        
        #   determine anchor
        px -= w
        py -= h
        if px - w < 0: px += w
        if py - h < 0: py += h
        return px, py, w, h
        
    #   ==========[ UPDATE ]==========
    def _update_colours(self) -> None:
        self._main_clr, self._bg_clr = config.main_clr, config.bg_clr
            
    def _update_text(self) -> None:
        
        self._title_surf = self._font.render(self.title, True, self._main_clr)
        self._title_rect = self._title_surf.get_rect(left=self.rect.left + 3 * self._radius, centery=self.rect.centery)
        self.btn_center = (self.rect.left + 1.5 * self._radius, self._title_rect.centery)
        
        if self._description:
            self._desc_rect = pg.Rect(self.get_desc_pos())
            self._symbol_surf = self._desc_font.render("?", True, self._main_clr)
            self._symbol_rect = self._symbol_surf.get_rect(center=self.btn_center)

    def update(self, *args, **kwargs) -> None:
        self._update_colours()
        self._update_text()
        
    
    #   ==========[ DRAW ]==========   
    def _draw_text(self, screen:pg.Surface) -> None:
        
        screen.blit(self._title_surf, self._title_rect)
        if self._description: screen.blit(self._symbol_surf, self._symbol_rect)
            
    def draw_description(self, screen:pg.Surface) -> None:
        
        #   draw background
        pg.draw.rect(screen, self._bg_clr, self._desc_rect)
        pg.draw.rect(screen, self._main_clr, self._desc_rect, self._border)
        
        #   draw texts
        topleft = self._desc_rect.topleft + 0.5 * self._padding
        for i, line in enumerate(self._description):
            surf = self._desc_font.render(line, True, self._main_clr)
            pos = topleft + self._desc_font.get_height() * i * np.array((0, 1))
            rect = surf.get_rect(topleft=pos)
            screen.blit(surf, rect)
    
    def draw(self, screen:pg.Surface) -> None:
        
        if self._description:
            pg.draw.circle(screen, self._bg_clr, self.btn_center, self._radius)
            pg.draw.circle(screen, self._main_clr, self.btn_center, self._radius, int(0.07 * self._desc_font.get_height()))
        self._draw_text(screen)