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
        self.values: list[float] = np.linspace(min_v, max_v, int(num_vals), dtype=Decimal).tolist()
        self.x_vals: list[int] = np.linspace(self.rect.left, self.rect.right, int(num_vals), dtype=np.int16).tolist()
        
        if dft not in self.values: raise ValueError(f"Invalid default value ({self.values=}, {dft=})")
        self.index = self.values.index(dft)
        self.value = float(self.values[self.index])
        self.x_pos = self.x_vals[self.index]
        self.radius = int(self.rect.height * 1.3)
        self.dragging = False
        
    
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return pg.Rect(self.rect.left, self.rect.centery - self.radius, self.rect.width, 2 * self.radius).collidepoint(mouse_pos)
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self.min_val_surf = self.font.render(str(self.values[0]), True, self.main_clr)
        self.max_val_surf = self.font.render(str(self.values[-1]), True, self.main_clr)
        self.val_surf = self.font.render(str(self.values[self.index]), True, self.main_clr)
        self.min_val_rect = self.min_val_surf.get_rect(right=self.rect.left - 2 * self.radius, centery=self.rect.centery)
        self.max_val_rect = self.max_val_surf.get_rect(left=self.rect.right + 2 * self.radius, centery=self.rect.centery)
        self.val_rect = self.val_surf.get_rect(top=self.rect.bottom + self.radius, centerx=self.x_vals[self.index])
        
    def update(self, hvr_id, hl_id) -> None:

        def is_between_vals(index):
            return self.x_vals[index] <= self.x_pos <= self.x_vals[index + 1]
        
        if self.x_pos < self.x_vals[0]: 
            self.index = 0
        elif self.x_pos > self.x_vals[-1]: 
            self.index = -1
        else:
            for i in range(len(self.x_vals) - 1):
                if is_between_vals(i):
                    self.index = i if abs(self.x_pos - self.x_vals[i]) < abs(self.x_pos - self.x_vals[i + 1]) else i + 1
                    break

        self.value = float(self.values[self.index])
        self._update_colours(hvr_id, hl_id)
        self._update_text()
            

    #   ==========[ DRAW ]==========
    def _draw_text(self, screen:pg.Surface) -> None:
        
        screen.blit(self.min_val_surf, self.min_val_rect)
        screen.blit(self.max_val_surf, self.max_val_rect)
        screen.blit(self.val_surf, self.val_rect)
    
    
    def draw(self, screen:pg.Surface) -> None:
        super().draw(screen)
        
        pg.draw.circle(screen, self.bg_clr, (self.x_vals[self.index], self.rect.centery), self.radius)
        pg.draw.circle(screen, self.main_clr, (self.x_vals[self.index], self.rect.centery), self.radius, self.border)