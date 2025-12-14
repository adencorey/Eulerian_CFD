import pygame as pg

from typing import Generator
import traceback
import logging
import sys

from cfd.settings.manager import settings
from cfd.interface.config import Events, Screens, Delay
from cfd.interface.screens import ToolBar, LibraryScreen, SettingsScreen, CreateProjectScreen, EditProjectScreen, SimulationScreen

logger = logging.getLogger(__name__)

class DelayQueue:
    
    def __init__(self) -> None:
        self._delays: list[Delay] = []
    
    def update(self) -> None:
        
        exausted: list[Delay] = []
        for delay in self._delays:
            try:
                next(delay)
            except StopIteration:
                exausted.append(delay)
        for delay in exausted:
            self._delays.remove(delay)
    
    def append(self, function:Generator) -> None:
        self._delays.append(function)

class App:
    
    def __init__(self, screen: pg.Surface) -> None:

        self.running = True
        self.screen: pg.Surface = screen
        self.delay_queue = DelayQueue()

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
        elif screen_id == Screens.SIMULATION.value:
            self.current_screen = SimulationScreen()
                
    #   mainloop
    def run(self):
        
        logger.info("Running mainloop...")
        keyboard_inp = ""
        max_char = 0
        dt = 1 / settings.tps
        while self.running:
            self.clock.tick(settings.tps)
            tps = self.clock.get_fps()
            interval = max(tps / settings.fps, 1)
            
            typing = False
            try:
                for event in pg.event.get():
                    self.tool_bar.handle_events(event)
                    self.current_screen.handle_events(event)
                    
                    if event.type == Events.CLEAR_INPUT: 
                        keyboard_inp = ""
                        
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
                    
                    if typing:                
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_BACKSPACE:
                                keyboard_inp = keyboard_inp[:-1]
                        if event.type == pg.TEXTINPUT:
                            if len(keyboard_inp) < max_char:
                                keyboard_inp += event.text
                        self.current_screen.handle_type(keyboard_inp)

                    if event.type == Events.DELAY_FUNCTION:
                        self.delay_queue.append(event.function)
            except Exception:
                traceback.print_exc()
                raise
                    
            self.current_screen.update(dt)
            self.delay_queue.update()
            
            if pg.time.get_ticks() % int(interval) == 0:
                self.tool_bar.update(tps / interval, tps)
                self.screen.fill(settings.theme.dark_bg)
                self.tool_bar.draw(self.screen)
                self.current_screen.draw(self.screen)
                pg.display.flip()
        
        logger.info("Shutting down program...")
        pg.quit()
        sys.exit()