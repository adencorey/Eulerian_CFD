import pygame as pg
import numpy as np

from fluid_sim.helper.assets import load_image, recolour_image
from fluid_sim.settings.themes import Theme


class Button:
    
    def __init__(self, name:str, rect: pg.Rect, text:str):
        
        self.name = name
        self.rect = rect
        self.text = text
        self.font = pg.font.SysFont("DejaVu Sans", 25)


class RectButton(Button):
    
    def __init__(self, name: str, rect: pg.Rect, text:str) -> None:
        super().__init__(name, rect, text)
    
    def draw(self, screen: pg.Surface, theme: Theme, hover_btn) -> None:
        
        if hover_btn == self.name:
            colour = theme.highlight
            bg = theme.hover
        else:
            colour = theme.main
            bg = theme.light_bg
        
        pg.draw.rect(screen, bg, self.rect)
        if self.text:
            text_surf: pg.Surface = self.font.render(self.text, True, colour)
            text_rect: pg.Rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)           


#   ==========[ QUIT BUTTON ]==========
class QuitButton(RectButton):
    
    def __init__(self, rect) -> None:
        super().__init__("quit-button", rect, "x")
        
    def draw(self, screen: pg.Surface, theme: Theme, hover_btn) -> None:
        
        if hover_btn == self.name:
            colour = theme.highlight
            bg = (255, 0, 0)
        else:
            colour = theme.main
            bg = theme.light_bg
        
        pg.draw.rect(screen, bg, self.rect)
        if self.text:
            text_surf: pg.Surface = self.font.render(self.text, True, colour)
            text_rect: pg.Rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)        


#   ==========[ SIDEBAR BUTTON ]==========
class SideBarButton(Button):
    
    def __init__(self, name:str, rect:pg.Rect, image:str, text:str="?") -> None:
        
        super().__init__(name, rect, text)
        
        self.center = rect.center
        self.radius = int(0.45 * self.rect.width)
        self.size = 0.6 * np.array(rect.size, dtype=np.uint16)
        
        self.image: pg.Surface = load_image(image)
        self.scaled_image = pg.transform.scale(self.image, self.size) if self.image else None
        if self.scaled_image:
            self.rect = self.scaled_image.get_rect(center=self.center)
        else:
            self.rect = pg.Rect((0, 0), self.size)
            self.rect.center = self.center

    def draw(self, screen: pg.Surface, theme: Theme, hover_btn) -> None:
        
        if hover_btn == self.name:
            pg.draw.circle(screen, theme.hover, self.center, self.radius)
            colour = theme.highlight
        else:
            colour = theme.main
        
        if self.scaled_image: 
            image: pg.Surface = recolour_image(self.scaled_image.copy(),  (0, 0, 0), colour)
            screen.blit(image, self.rect)
        else:
            pg.draw.rect(screen, colour, self.rect, 1)
            text_surf = self.font.render(self.text, True, colour)
            text_rect = text_surf.get_rect(center = self.center)
            screen.blit(text_surf, text_rect)
        
    def collide(self, mouse_pos) -> True | False:
        
        mx, my = mouse_pos
        return (self.center[0] - mx) ** 2 + (self.center[1] - my) ** 2 <= (self.radius) ** 2