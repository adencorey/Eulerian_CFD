import pygame as pg

import logging
import sys

from cfd.settings.manager import settings
from cfd.interface.config import Events, Screens
from cfd.interface.screens import ToolBar, LibraryScreen, SettingsScreen, CreateProjectScreen, EditProjectScreen

logger = logging.getLogger(__name__)

class App:
    
    def __init__(self, screen: pg.Surface) -> None:

        self.running = True
        self.screen: pg.Surface = screen

        self.clock: pg.time.Clock = pg.time.Clock()
        self.current_screen = LibraryScreen()
        self.tool_bar = ToolBar()
        
    def set_screen(self, screen_id, highlighting) -> None:
        
        if screen_id == Screens.LIBRARY.value:
            self.current_screen = LibraryScreen()
        elif screen_id == Screens.CRT_PROJ.value:
            self.current_screen = CreateProjectScreen()
        elif screen_id == Screens.EDIT_PROJ.value:
            self.current_screen = EditProjectScreen(highlighting)
        elif screen_id == Screens.SETTINGS.value:
            self.current_screen = SettingsScreen()
                
    #   mainloop
    def run(self):
        
        logger.info("Running mainloop...")
        keyboard_inp = ""
        max_char = 0
        while self.running:
            typing = False
            for event in pg.event.get():
                self.tool_bar.handle_events(event)
                self.current_screen.handle_events(event)
                
                if event.type == Events.CLEAR_INPUT: keyboard_inp = ""
                if event.type == Events.KEYBOARD_INPUT: 
                    typing = True
                    max_char = event.max_char
                
                if event.type == pg.QUIT or event.type == Events.QUIT_PROGRAM:
                    self.running = False
                
                if event.type == Events.SCREEN_SWITCH:
                    try:
                        highlighting = event.highlighting
                    except:
                        highlighting = None
                    self.set_screen(event.screen_id, highlighting)
                
                if typing and event.type == pg.KEYDOWN:
                    
                    if event.key == pg.K_BACKSPACE:
                        keyboard_inp = keyboard_inp[:-1]
                    elif len(keyboard_inp) < max_char:
                        keyboard_inp += event.unicode

                    self.current_screen.handle_type(keyboard_inp)
                    
            
            self.current_screen.update()
            self.tool_bar.update(self.clock.get_fps())

            self.screen.fill(settings.theme.dark_bg)
            self.tool_bar.draw(self.screen)
            self.current_screen.draw(self.screen)
            
            pg.display.update()
            self.clock.tick(settings.fps)
        
        logger.info("Shutting down program...")
        pg.quit()
        sys.exit()