import pygame as pg

import logging
import sys

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import AppScreens, Events, config
from fluid_sim.interface.screens import ToolBar, LibraryScreen, SettingsScreen

logger = logging.getLogger(__name__)

class App:
    
    def __init__(self, screen: pg.Surface) -> None:

        self.running = True
        self.screen: pg.Surface = screen

        self.clock: pg.time.Clock = pg.time.Clock()
        self.current_screen = LibraryScreen()
        self.tool_bar = ToolBar()
        
    def set_screen(self, app_screen: AppScreens) -> None:
        
        match app_screen:
            
            case AppScreens.LIBRARY:
                self.current_screen = LibraryScreen()
            case AppScreens.SETTINGS:
                self.current_screen = SettingsScreen()
                
    #   mainloop
    def run(self):
        
        logger.info("Running mainloop...")
        while self.running:
            for event in pg.event.get():
                self.tool_bar.handle_events(event)
                self.current_screen.handle_events(event)
                
                if event.type == pg.QUIT or event.type == Events.QUIT_PROGRAM:
                    self.running = False
                
                if event.type == Events.SCREEN_SWITCH:
                    self.set_screen(AppScreens(event.screen_id))
            
            self.current_screen.update()
            self.tool_bar.update(self.clock.get_fps())

            self.screen.fill(settings.theme.dark_bg)
            self.current_screen.draw(self.screen)
            self.tool_bar.draw(self.screen)
            
            pg.display.update()
            self.clock.tick(settings.fps)
        
        logger.info("Shutting down program...")
        pg.quit()
        sys.exit()