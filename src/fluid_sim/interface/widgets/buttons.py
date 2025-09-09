import pygame as pg
import numpy as np

from fluid_sim.utilities.assets import load_image, recolour_image
from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import config, Widget
        

class RectButton(Widget):
    
    def __init__(self, name: str, rect: pg.Rect, colours:tuple[tuple, tuple]=None, text:str=None, font:pg.font.Font=None) -> None:
        super().__init__(name, rect, colours, text, font)
    
    def draw(self, screen: pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        super()._draw_text(screen)


#   ==========[ QUIT BUTTON ]==========
class QuitButton(RectButton):
    
    def __init__(self, rect) -> None:
        super().__init__(name="quit-button", rect=rect, text="x", font=config.font["sub"])
        
    def _update_colours(self, hovering) -> None:
        
        super()._update_colours(hovering)
        if hovering == self.name: self.bg_clr = (255, 0, 0)
        

#   ==========[ SIDEBAR BUTTON ]==========
class SideBarButton(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, image:str) -> None:
        
        super().__init__(name=name, rect=rect, text="?")
        
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
    def update(self, hovering:str) -> None:
        
        super().update(hovering)
        self.hovering = True if hovering == self.name else False
                    

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