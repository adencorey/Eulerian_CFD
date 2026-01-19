import pygame as pg

from enum import Enum
import time
from typing import Generator
from types import FunctionType

from cfd.settings.manager import settings


#   ==========[ SCREEN IDs ]==========
class Screens(Enum):
    LIBRARY = 0
    CRT_PROJ = 1
    EDIT_PROJ = 2
    SETTINGS = 3
    SIMULATION = 4
    
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
    CLEAR_INPUT = pg.USEREVENT + 4
    DELAY_FUNCTION = pg.USEREVENT + 5


#   ==========[ CONFIGURATIONS ]==========
class Config:
    
    def __init__(self, width=1980, height=1080) -> None:
        
        pg.font.init()
        
        self.width = width
        self.height = height
        
        DEJAVU = "DejaVu Sans"
        TIMES = "Times"
        ARIAL = "Arial"
        self.font = {
            "title" : pg.font.SysFont(DEJAVU, int(0.04 * height)),
            "head"  : pg.font.SysFont(DEJAVU, int(0.03 * height)),
            "body"  : pg.font.SysFont(TIMES, int(0.028 * height)),
            "par"   : pg.font.SysFont(TIMES, int(0.024 * height)),
            "sub"   : pg.font.SysFont(ARIAL, int(0.024 * height)),
            "sml"   : pg.font.SysFont(ARIAL, int(0.0175 * height))
        }
        
        self.update()
        
    def update(self) -> None:
        
        theme = settings.theme
        self.main_clr, self.secondary_clr, self.bg_clr = theme.main, theme.secondary, theme.light_bg
        self.hl_clr, self.hvr_clr = theme.highlight, theme.hover
config = Config()


#   ==========[ DELAY CLASS ]==========
class Delay:
    """async delay class"""
    
    def __init__(self, duration:float, action:FunctionType=None):
        
        self.start = time.time()
        self.duration = duration
        self.action = action
    
    def __iter__(self) -> Generator:
        """check if timer is finished, pauses and yields back to main caller if not finished"""
        
        while time.time() - self.start <= self.duration:
            if self.action: self.action()
            yield