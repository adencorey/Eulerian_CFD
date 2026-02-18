import pygame as pg
import numpy as np

from cfd.interface.config import config
from .widget import Widget, NULLWIDGET


class Dropdown(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, options:list[str], setting, font=config.font["body"], anchor:str=None) -> None:
        
        self.text = self.get_selected(setting)
        super().__init__(name=name, rect=rect, anchor=anchor, text=self.text, font=font)
        
        self.show = False
        self.hovering: DropdownChild = NULLWIDGET
        
        self._arrow_rect = pg.Rect(self.rect.topright, (int(0.8 * self.rect.height), self.rect.height))
        
        self._children: list[DropdownChild] = []
        for i in range(len(options)):
            self._children.append(DropdownChild(
                name=f"{self.name}.{options[i]}",
                rect=rect.copy().move(0, (i + 1) * rect.height),
                text=options[i].capitalize(),
                font=self._font
            ))
    
    #   ==========[ UTILITIES ]==========
            
    def get_selected(self, setting) -> str:
        return str(setting).capitalize()
    
    def collide(self, mouse_pos) -> True | False:
        if self.rect.collidepoint(mouse_pos) or self._arrow_rect.collidepoint(mouse_pos):
            self.hovering = NULLWIDGET
            return True
        return False
    
    def collide_children(self, mouse_pos) -> True | False:
        
        if self.show:
            for child in self._children:
                if child.collide(mouse_pos):
                    self.hovering = child
                    return True
        self.hovering = NULLWIDGET
        return False
    
    def clicked(self, setting) -> None:
        
        self.show = False
        self.text = self.get_selected(setting)
        
        
    #   ==========[ UPDATE ==========    
    def update(self, hvr_id, hl_id):
        
        super().update(hvr_id, -1)
        for child in self._children:
            child.update(self.hovering.name, "None")


    #   ==========[ DRAW ]==========
    def _draw_arrow(self, screen:pg.Surface) -> None:
        
        center = np.array(self._arrow_rect.center, dtype=np.float16)
        
        #   rect
        pg.draw.rect(screen, self._bg_clr, self._arrow_rect)
        pg.draw.rect(screen, self._main_clr, self._arrow_rect, self._border)
        
        #   arrow
        len = int(0.25 * self._arrow_rect.height)
        sign = -1 if self.show else 1
        points = []
        for i in range(3):
            rad = np.deg2rad(i * 120)
            coord = center + len * np.array((np.sin(rad), sign * np.cos(rad)), dtype=np.float16)
            points.append(coord.astype(np.int16))
            
        pg.draw.polygon(screen, self._main_clr, points)
    
    def draw_children(self, screen:pg.Surface) -> None:
        
        for child in self._children:
            child.draw(screen)
    
    def draw_parent(self, screen:pg.Surface) -> None:
        
        self._draw_arrow(screen)
        self.draw(screen)
        
        
class DropdownChild(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, text:str, font) -> None:
        super().__init__(name=None, rect=rect, text=text, font=font)
        self.name = name
        
    def _update_colours(self, hvr_name, hl_name):

        if self.name == hl_name:
            self._main_clr, self._bg_clr = config.secondary_clr, config.bg_clr
        elif self.name == hvr_name:
            self._main_clr, self._bg_clr = config.hl_clr, config.hvr_clr
        else:
            self._main_clr, self._bg_clr = config.main_clr, config.bg_clr