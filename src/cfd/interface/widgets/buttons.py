import pygame as pg
import numpy as np

from enum import Enum

from cfd.utilities.assets import load_image, recolour_image
from cfd.interface.config import registry, config
from cfd.interface.widgets.widget import Widget
        

class RectButton(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, colours:tuple[tuple, tuple]=None, text:str=None, font:pg.font.Font=None) -> None:
        super().__init__(name=name, rect=rect, colours=colours, text=text, font=font)
        

#   ==========[ WINDOW BUTTON ]==========
class WindowButton(RectButton):
    
    def __init__(self, name:str, rect:pg.Rect, symbol:str) -> None:
        super().__init__(name=name, rect=rect, text=symbol, font=config.font["sub"])
        
    def _update_colours(self, hvr_id:int, hl_id:int) -> None:
        
        super()._update_colours(hvr_id, hl_id)
        if hvr_id == self.id and self.id == registry.ids["quit_btn"]: self.bg_clr = (255, 0, 0)
        
    def draw(self, screen: pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        super()._draw_text(screen)

#   ==========[ SIDEBAR BUTTON ]==========
class SideBarButton(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, image:str) -> None:
        super().__init__(name=name, rect=rect, text="?")
        
        self.center = rect.center
        self.radius = int(0.45 * self.rect.width)
        self.size = 0.6 * np.array(rect.size)
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
    

#   ==========[ PROJECT BUTTONS ]==========
class ProjectButton(Widget):
    
    def __init__(self, info, rect, text, metadata:dict):
        super().__init__(info, rect, text, font=config.font["head"])
        
        self.metadata = metadata
        self.sub_font = config.font["sub"]
        self.offset = int(0.1 * self.rect.height)
        
    
    def _update_text(self):
        super()._update_text()
        
        self.text_rect = self.text_surf.get_rect(topleft=self.rect.topleft + self.offset * np.array((1, 1)))
        self.sub_texts: list = []
        for i in range(len(self.metadata)):
            surf = self.sub_font.render(self.metadata[i], True, self.main_clr)
            rect = surf.get_rect(bottomleft=self.rect.bottomleft + self.offset * np.array((i + 1, -1)))
            self.sub_texts.append(surf, rect)
    
    def _draw_text(self, screen):
        super()._draw_text(screen)
        
        for surf, rect in self.sub_texts:
            screen.blit(surf, rect)