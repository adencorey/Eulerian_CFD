import pygame as pg

from enum import Enum
import logging
import sys

from fluid_sim.ui.main_menu import MainMenu
from fluid_sim.ui.tool_bar import ToolBar
from fluid_sim.settings import Settings

logger = logging.getLogger(__name__)

#   indexing screens
class AppScreens(Enum):
    
    MAIN_MENU = 0
    SETTINGS = 1
    CANVAS = 2


class App:
    
    def __init__(self, screen: pg.Surface, settings: Settings) -> None:
        
        self.screen: pg.Surface = screen
        self.width, self.height = self.screen.get_size()
        self.settings = settings
        
        self.clock: pg.time.Clock = pg.time.Clock()
        self.current_screen = MainMenu(self)
        self.tool_bar = ToolBar(settings=self.settings, screen_width=self.width)
        
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
                        
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        self.settings.theme_name = "light" if self.settings.theme_name == "dark" else "dark"
                    if event.key == pg.K_SPACE:
                        self.settings.save()
            
            self.tool_bar.update()

            self.screen.fill(self.settings.theme.background)
            self.current_screen.draw()
            self.tool_bar.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.settings.fps)
        
        logger.info("Shutting down program...")
        pg.quit()
        sys.exit()