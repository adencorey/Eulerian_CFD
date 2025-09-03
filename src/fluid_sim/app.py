import pygame as pg

from enum import Enum
import logging
import sys

from .ui.main_menu import MainMenu
from .ui.tool_bar import ToolBar

logger = logging.getLogger(__name__)

#   indexing screens
class AppScreens(Enum):
    
    MAIN_MENU = 0
    SETTINGS = 1
    CANVAS = 2


class App:
    
    def __init__(self, screen: pg.Surface) -> None:
        
        self.screen: pg.Surface = screen
        self.width, self.height = self.screen.get_size()
        self.bg_colour = (50, 50, 50)
        
        self.clock: pg.time.Clock = pg.time.Clock()
        self.current_screen = MainMenu(self)
        self.tool_bar = ToolBar(bg_colour=self.bg_colour, screen_width=self.width)
        
    def set_screen(self, app_screen: AppScreens) -> None:
        
        match app_screen:
            
            case AppScreens.MAIN_MENU:
                self.current_screen = MainMenu(self)
                
    #   mainloop
    def run(self):
        
        running = True
        logger.info("Running mainloop...")
        while running:
            for event in pg.event.get():
                
                self.current_screen.handle_events(event)
                action: str = self.tool_bar.handle_events(event)
                
                match action:
                    case "quit":
                        running = False
                    case "minimise":
                        pg.display.iconify()
                        logger.info("Minimised screen")

            self.screen.fill(self.bg_colour)
            self.current_screen.draw()
            self.tool_bar.draw(self.screen)
            pg.display.update()
        
        logger.info("Shutting down program...")
        pg.quit()
        logger.info("Quitted Pygame")
        sys.exit()