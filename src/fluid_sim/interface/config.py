import pygame as pg

from enum import Enum

from fluid_sim.settings.manager import settings


#   ==========[ SCREEN IDs ]==========
class AppScreens(Enum):
    
    LIBRARY = 0
    CREATE_PROJECT = 2
    SETTINGS = 1
    
#   ===========[ WIDGET IDs ]==========
class AppWidgets(Enum):
    
    #   tool bar
    QUIT_BTN = 0
    MIN_BTN = 1
    LIBRARY_BTN = 2
    SETTINGS_BTN = 3

    #   library
    CREATE_BTN = 4
    
    #   create project
    BACK_BTN = 8
    PROJ_NAME_TEXT = 9

    #   settings
    THEME_DROP = 5
    FPS_DROP = 6
    SHOW_FPS_DROP = 7


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
        self.main_clr, self.secondary_clr, self.bg_clr = theme.main, theme.secondary, theme.light_bg
        self.hl_clr, self.hvr_clr = theme.highlight, theme.hover
    
config = Config()


#   ==========[ WIDGET ]==========
class Widget:
    
    def __init__(self, info:Enum|None, rect:pg.Rect, colours:tuple[tuple, tuple]=None, text:str=None, font:pg.font.Font=None) -> None:
        
        if info:
            self.name: str = info.name.lower()
            self.id: int = info.value
        else:
            self.id: int = None
        self.rect = rect
        self.text = text
        self.font = font if font else config.font["body"]
        self.border = int(0.05 * self.rect.height)
        self.main_clr, self.bg_clr = colours if colours else config.main_clr, config.bg_clr
            

    #   ==========[ UPDATE ]==========
    def _update_colours(self, hvr_id:int, hl_id:int) -> None:

        if self.id == hl_id:
            self.main_clr, self.bg_clr = config.secondary_clr, config.bg_clr
        elif self.id == hvr_id:
            self.main_clr, self.bg_clr = config.hl_clr, config.hvr_clr
        else:
            self.main_clr, self.bg_clr = config.main_clr, config.bg_clr
            
    def _update_text(self) -> None:
        
        self.text_surf = self.font.render(self.text, True, self.main_clr)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
    def update(self, hvr_id:int, hl_id:int) -> None:

        self._update_colours(hvr_id, hl_id)
        if self.text: self._update_text()
        
    
    #   ==========[ DRAW ]==========
    def _draw_text(self, screen:pg.Surface) -> None:
        if self.text: screen.blit(self.text_surf, self.text_rect)
    
    def draw(self, screen:pg.Surface) -> None:
        
        pg.draw.rect(screen, self.bg_clr, self.rect)
        pg.draw.rect(screen, self.main_clr, self.rect, self.border)
        self._draw_text(screen)
        
    #   ==========[ UTILS ]==========
    def collide(self, mouse_pos) -> True | False:
        return self.rect.collidepoint(mouse_pos)
    
class NullWidget:
    
    id = None
    name = None
NULLWIDGET = NullWidget()