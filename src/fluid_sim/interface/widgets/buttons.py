import pygame as pg
import numpy as np

from enum import Enum

from fluid_sim.utilities.assets import load_image, recolour_image
from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import config, Widget
        

class RectButton(Widget):
    
    def __init__(self, info:Enum, rect:pg.Rect, colours:tuple[tuple, tuple]=None, text:str=None, font:pg.font.Font=None) -> None:
        super().__init__(info=info, rect=rect, colours=colours, text=text, font=font)
    
    def draw(self, screen: pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        pg.draw.rect(screen, self.main_clr, self.rect, self.border)
        super()._draw_text(screen)


#   ==========[ WINDOW BUTTON ]==========
class WindowButton(RectButton):
    
    def __init__(self, info:Enum, rect:pg.Rect, symbol:str) -> None:
        super().__init__(info=info, rect=rect, text=symbol, font=config.font["sub"])
        
    def _update_colours(self, hvr_id:int, hl_id:int) -> None:
        
        super()._update_colours(hvr_id, hl_id)
        if hvr_id == self.id: self.bg_clr = (255, 0, 0)
        
    def draw(self, screen: pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        super()._draw_text(screen)

#   ==========[ SIDEBAR BUTTON ]==========
class SideBarButton(Widget):
    
    def __init__(self, info:Enum, rect:pg.Rect, image:str) -> None:
        
        super().__init__(info=info, rect=rect, text="?")
        
        self.center = rect.center
        self.radius = int(0.45 * self.rect.width)
        self.size = 0.6 * np.array(rect.size, dtype=np.uint16)
        self.hovering = False
        
        #   load and scale image
        self.image: pg.Surface = load_image(image)
        self.scaled_image = pg.transform.scale(self.image, self.size) if self.image else None
        if self.scaled_image:
            self.rect = self.scaled_image.get_rect(center=self.center)
        else:
            self.rect = pg.Rect((0, 0), self.size)
            self.rect.center = self.center
            
    
    #   ==========[ UPDATE ]==========
    def update(self, hvr_id:int, hl_id:int) -> None:
        
        super().update(hvr_id, hl_id)
        self.hovering = True if hvr_id == self.id else False
                    

    def draw(self, screen:pg.Surface) -> None:
        
        if self.hovering: pg.draw.circle(screen, self.bg_clr, self.center, self.radius)
        
        if self.scaled_image: 
            image: pg.Surface = recolour_image(self.scaled_image.copy(),  (0, 0, 0), self.main_clr)
            screen.blit(image, self.rect)
        else:
            #   draw "?" if image file is missing
            pg.draw.rect(screen, self.main_clr, self.rect, 1)
            self._draw_text(screen)
        
    def collide(self, mouse_pos) -> True | False:
        
        mx, my = mouse_pos
        return (self.center[0] - mx) ** 2 + (self.center[1] - my) ** 2 <= (self.radius) ** 2