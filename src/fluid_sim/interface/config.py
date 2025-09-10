import pygame as pg

from enum import Enum

from fluid_sim.settings.manager import settings


#   ==========[ SCREEN IDs ]==========
class AppScreens(Enum):
    
    LIBRARY = 0
    SETTINGS = 1
    CANVAS = 2


#   ==========[ CUSTOM PYGAME EVENT IDs ]==========
class Events:
    QUIT_PROGRAM = pg.USEREVENT + 1
    SCREEN_SWITCH = pg.USEREVENT + 2


#   ==========[ CONFIGURATIONS ]==========
class Config:
    
    def __init__(self, width=1980, height=1080) -> None:
        
        pg.font.init()
        
        self.width = width
        self.height = height
        
        self.font_name = "DejaVu Sans"
        self.body_font_name = "Times"
        self.font = {
            "title" : pg.font.SysFont(self.font_name, int(0.04 * height)),
            "head"  : pg.font.SysFont(self.font_name, int(0.03 * height)),
            "body"  : pg.font.SysFont(self.body_font_name, int(0.03 * height)),
            "par"   : pg.font.SysFont(self.body_font_name, int(0.02 * height)),
            "sub"   : pg.font.SysFont(self.font_name, int(0.025 * height))
        }
        
        self.update()
        
    def update(self) -> None:
        
        theme = settings.theme
        self.main_clr, self.bg_clr = theme.main, theme.light_bg
        self.hl_clr, self.hvr_clr = theme.highlight, theme.hover
    
config = Config()


#   ==========[ WIDGET ]==========
class Widget:
    
    def __init__(self, name:str, rect:pg.Rect, colours:tuple[tuple, tuple]=None, text:str=None, font:pg.font.Font=config.font["body"]) -> None:
        
        self.name = name
        self.rect = rect
        self.text = text
        self.font = font
        self.border = int(0.05 * self.rect.height)
        self.main_clr, self.bg_clr = colours if colours else config.main_clr, config.bg_clr
        
        if text and isinstance(text, str):
            self._update_text()
            self.text_rect = self.text_surf.get_rect(center=rect.center)
    

    #   ==========[ UPDATE ]==========
    def _update_colours(self, hovering:str) -> None:
        
        if hovering == self.name:
            self.main_clr, self.bg_clr = config.hl_clr, config.hvr_clr
        else:
            self.main_clr, self.bg_clr = config.main_clr, config.bg_clr
            
    def _update_text(self) -> None:
        
        self.text_surf = self.font.render(self.text, True, self.main_clr)
        
    def update(self, hovering:str) -> None:
        
        self._update_colours(hovering)
        if self.text and isinstance(self.text, str): self._update_text()
        
    
    #   ==========[ DRAW ]==========
    def _draw_text(self, screen:pg.Surface) -> None:
        
        if self.text and isinstance(self.text, str): screen.blit(self.text_surf, self.text_rect)