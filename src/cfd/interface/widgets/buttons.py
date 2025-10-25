import pygame as pg
import numpy as np

from cfd.utilities.assets import load_image, recolour_image
from cfd.interface.config import registry, config
from .widget import Widget
        

class RectButton(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, anchor:str=None, colours:tuple=None, text:str=None, font:pg.font.Font=None, disabled=False) -> None:
        super().__init__(name=name, rect=rect, anchor=anchor, colours=colours, text=text, font=font)
        self.disabled = disabled

    def _update_colours(self, hvr_id, hl_id):
        super()._update_colours(hvr_id, hl_id)
        if self.disabled:
            self.main_clr, self.bg_clr = config.hvr_clr, config.bg_clr
        

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
    
    def __init__(self, name:str, rect:pg.Rect, anchor:str=None, image:str=None) -> None:
        super().__init__(name=name, rect=rect, anchor=anchor, text="?")
        
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
        return (self.center[0] - mouse_pos[0]) ** 2 + (self.center[1] - mouse_pos[1]) ** 2 <= (self.radius) ** 2
    

#   ==========[ PROJECT BUTTONS ]==========
class ProjectButton(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, text:str, metadata:dict[str, str]):
        super().__init__(name=name, rect=rect, text=text, font=config.font["head"])
        
        self.metadata = metadata
        self.sub_font = config.font["sub"]
        self.offset = int(0.1 * self.rect.height)
        
    
    def _update_text(self):
        super()._update_text()
        
        self.text_rect = self.text_surf.get_rect(topleft=self.rect.topleft + self.offset * np.array((1, 1)))
        self.sub_texts: list = []
        i = 0
        for key, val in self.metadata.items():
            text = f"{key.replace('_', ' ')}: {val}"
            surf = self.sub_font.render(text, True, self.main_clr)
            rect = surf.get_rect(bottomleft=self.rect.bottomleft + self.offset * np.array((1 + i, -1)))
            self.sub_texts.append((surf, rect))
            i += 50
    
    def _draw_text(self, screen):
        super()._draw_text(screen)
        
        for surf, rect in self.sub_texts:
            screen.blit(surf, rect)