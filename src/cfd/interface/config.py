import pygame as pg

from enum import Enum

from cfd.settings.manager import settings


#   ==========[ SCREEN IDs ]==========
class Screens(Enum):
    
    LIBRARY = 0
    CRT_PROJ = 2
    SETTINGS = 1

    
#   ==========[ OBJECT REGISTRY ]==========
class WidgetRegister:
    
    def __init__(self):
        
        self.ids: dict[str, int] = {}
        self.nxt_id = 0
    
    def register(self, name:str) -> list[str, int]:
        """Register widget to dictionary with name, returns name and ID"""
        
        if name not in self.ids:
            self.ids[name] = id = self.nxt_id
            self.nxt_id += 1
        else: id = self.ids[name]
        return name, id
    
    def unregister(self, id) -> None:
        """Unregister widget using ID"""
        
        key = next((val for _, val in self.ids.items() if val == id), None)
        if key: self.ids.pop(key)
registry = WidgetRegister()


#   ==========[ CUSTOM PYGAME EVENT IDs ]==========
class Events:
    QUIT_PROGRAM = pg.USEREVENT + 1
    SCREEN_SWITCH = pg.USEREVENT + 2
    KEYBOARD_INPUT = pg.USEREVENT + 3


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