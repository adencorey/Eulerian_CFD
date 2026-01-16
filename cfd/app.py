import pygame as pg

from typing import Generator
import traceback
import logging
import sys

from cfd.settings.manager import settings
from cfd.helpers.files import Project
from cfd.interface.config import Events, Screens, Delay
from cfd.interface.widgets import Widget, NULLWIDGET, TextBox
from cfd.interface.screens import *

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
        
        self.hovering: Widget = NULLWIDGET
        self.selected: TextBox = NULLWIDGET
        self.highlighted: Widget = NULLWIDGET
        self.project: Project = None
        self.keyboard_inp = ""
        self.max_char = -1

        self.clock: pg.time.Clock = pg.time.Clock()
        self.current_screen = LibraryScreen(self)
        self.tool_bar = ToolBar()
        
    def set_screen(self, screen_id) -> None:
        
        if screen_id == Screens.LIBRARY.value:
            self.current_screen = LibraryScreen(self)
        elif screen_id == Screens.CRT_PROJ.value:
            self.current_screen = CreateProjectScreen(self)
        elif screen_id == Screens.EDIT_PROJ.value:
            self.current_screen = EditProjectScreen(self)
        elif screen_id == Screens.SETTINGS.value:
            self.current_screen = SettingsScreen(self)
        elif screen_id == Screens.SIMULATION.value:
            self.current_screen = SimulationScreen(self)
        elif screen_id == Screens.CONFIG_INIT_PARAM.value:
            self.current_screen = ConfigInitParamScreen(self)
                
    #   mainloop
    def run(self):
        
        logger.info("Running mainloop...")

        while self.running:
            self.clock.tick(settings.fps)
            fps = self.clock.get_fps()
            
            if not self.selected.id: self.keyboard_inp = ""
            typing = False
            for event in pg.event.get():
                self.tool_bar.handle_events(event)
                self.current_screen.handle_events(event)
                    
                if event.type == Events.KEYBOARD_INPUT: 
                    typing = True
                    self.max_char = event.max_char
                
                if event.type == pg.QUIT or event.type == Events.QUIT_PROGRAM:
                    self.running = False
                
                if event.type == Events.SCREEN_SWITCH:                        
                    self.set_screen(event.screen_id)
                
                if typing:                
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_BACKSPACE:
                            self.keyboard_inp = self.keyboard_inp[:-1]
                    if event.type == pg.TEXTINPUT:
                        if len(self.keyboard_inp) < self.max_char:
                            self.keyboard_inp += event.text
                    self.selected.text = self.keyboard_inp

                if event.type == Events.DELAY_FUNCTION:
                    self.delay_queue.append(event.function)
                    
            self.current_screen.update()
            self.delay_queue.update()

            self.tool_bar.update(fps)
            self.screen.fill(settings.theme.dark_bg)
            self.tool_bar.draw(self.screen)
            self.current_screen.draw(self.screen)
            pg.display.flip()
        
        logger.info("Shutting down program...")
        pg.quit()
        sys.exit()