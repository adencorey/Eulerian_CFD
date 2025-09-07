import pygame as pg

from enum import Enum

#   ==========[ SCREEN IDs ]==========
class AppScreens(Enum):
    
    LIBRARY = 0
    SETTINGS = 1
    CANVAS = 2


#   ==========[ CUSTOM PYGAME EVENT IDs ]==========
QUIT_PROGRAM = pg.USEREVENT + 1
SCREEN_SWITCH = pg.USEREVENT + 2