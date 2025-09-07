import pygame as pg

import logging
import sys

from fluid_sim.settings.manager import Settings
from fluid_sim.ui.constants import *
from fluid_sim.ui.tool_bar import ToolBar
from fluid_sim.ui.library import LibraryScreen
from fluid_sim.ui.settings import SettingsScreen

logger = logging.getLogger(__name__)

class App:
    
    def __init__(self, screen: pg.Surface, settings: Settings) -> None:
        
        self.running = True
        self.screen: pg.Surface = screen
        self.width, self.height = self.screen.get_size()
        self.settings = settings
        
        self.clock: pg.time.Clock = pg.time.Clock()
        self.current_screen = LibraryScreen(self.width, self.height)
        self.tool_bar = ToolBar(self.settings, self.width, self.height)
        
    def set_screen(self, app_screen: AppScreens) -> None:
        
        match app_screen:
            
            case AppScreens.LIBRARY:
                self.current_screen = LibraryScreen(self.width, self.height)
            case AppScreens.SETTINGS:
                self.current_screen = SettingsScreen(self.width, self.height)
                
    #   mainloop
    def run(self):
        
        logger.info("Running mainloop...")
        while self.running:
            for event in pg.event.get():
                self.tool_bar.handle_events(event)
                self.current_screen.handle_events(event)
                
                if event.type == pg.QUIT or event.type == QUIT_PROGRAM:
                    self.running = False
                
                if event.type == SCREEN_SWITCH:
                    self.set_screen(AppScreens(event.screen_id))
                        
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        self.settings.theme_name = "light" if self.settings.theme_name == "dark" else "dark"
                        self.settings.save()
            
            self.tool_bar.update()

            self.screen.fill(self.settings.theme.dark_bg)
            self.current_screen.draw(self.screen)
            self.tool_bar.draw(self.screen)
            
            pg.display.update()
            self.clock.tick(self.settings.fps)
        
        logger.info("Shutting down program...")
        pg.quit()
        sys.exit()