import pygame as pg
import numpy as np

from decimal import Decimal

from cfd.interface.config import config
from .widget import Widget

class Slidebar(Widget):
    
    def __init__(self, name:str, rect:pg.Surface, min_val:float, max_val:float, step:float, default:float, font=config.font["sub"]) -> None:
        super().__init__(name=name, rect=rect, font=font, anchor="center")

        min_v, max_v, s, dft = Decimal(str(min_val)), Decimal(str(max_val)), Decimal(str(step)), Decimal(str(default))
        if s <= 0: raise ValueError("val_step must be greater than zero")
        val_range = max_v - min_v
        num_vals = val_range / s + 1
        if num_vals != num_vals.to_integral_value(): raise ValueError(f"Step must be divisible by range (range={max_v}-{min_v}={val_range}, {s=})")
        
        #   generate all values and x positions of slide bar
        self._values: list[float] = np.linspace(min_v, max_v, int(num_vals), dtype=Decimal).tolist()
        self._x_vals: list[int] = np.linspace(self.rect.left, self.rect.right, int(num_vals), dtype=np.int16).tolist()
        
        if dft not in self._values: raise ValueError(f"Invalid default value ({self._values=}, {dft=})")
        self._index = self._values.index(dft)
        self.value = float(self._values[self._index])
        self.x_pos = self._x_vals[self._index]
        self._radius = int(self.rect.height * 1.3)
        self.dragging = False
        
    
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return pg.Rect(self.rect.left, self.rect.centery - self._radius, self.rect.width, 2 * self._radius).collidepoint(mouse_pos)
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self._min_val_surf = self._font.render(str(self._values[0]), True, self._main_clr)
        self._max_val_surf = self._font.render(str(self._values[-1]), True, self._main_clr)
        self._min_val_rect = self._min_val_surf.get_rect(right=self.rect.left - 2 * self._radius, centery=self.rect.centery)
        self._max_val_rect = self._max_val_surf.get_rect(left=self.rect.right + 2 * self._radius, centery=self.rect.centery)
        self._val_surf = self._font.render(str(self._values[self._index]), True, self._main_clr)
        self._val_rect = self._val_surf.get_rect(top=self.rect.bottom + self._radius, centerx=self._x_vals[self._index])
        
    def update(self, hvr_id, hl_id) -> None:

        def is_between_vals(_index):
            return self._x_vals[_index] <= self.x_pos <= self._x_vals[_index + 1]
        
        if self.x_pos < self._x_vals[0]: 
            self._index = 0
        elif self.x_pos > self._x_vals[-1]: 
            self._index = -1
        else:
            for i in range(len(self._x_vals) - 1):
                if is_between_vals(i):
                    self._index = i if abs(self.x_pos - self._x_vals[i]) < abs(self.x_pos - self._x_vals[i + 1]) else i + 1
                    break

        self.value = float(self._values[self._index])
        self._update_colours(hvr_id, hl_id)
        self._update_text()
            

    #   ==========[ DRAW ]==========
    def _draw_text(self, screen:pg.Surface) -> None:
        
        screen.blit(self._min_val_surf, self._min_val_rect)
        screen.blit(self._max_val_surf, self._max_val_rect)
        screen.blit(self._val_surf, self._val_rect)
    
    
    def draw(self, screen:pg.Surface) -> None:
        super().draw(screen)
        
        pg.draw.circle(screen, self._bg_clr, (self._x_vals[self._index], self.rect.centery), self._radius)
        pg.draw.circle(screen, self._main_clr, (self._x_vals[self._index], self.rect.centery), self._radius, self._border)