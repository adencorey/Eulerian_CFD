import pygame as pg

import logging

from fluid_sim.settings import Settings

logger = logging.getLogger(__name__)


class ToolBar:
    
    def __init__(self, settings: Settings, screen_width) -> None:
        
        self.settings = settings
        self.screen_width = screen_width
        self.button_width = 0.03 * self.screen_width
        self.button_height = 0.02 * self.screen_width
        
        #   ==========[ BUTTONS ]==========
        self.quit_button = pg.Rect(self.screen_width - self.button_width, 0, self.button_width, self.button_height)
        self.min_button = pg.Rect(self.screen_width - 2 * self.button_width, 0, self.button_width, self.button_height)
        
        #   symbols
        self.font = pg.font.SysFont("DejaVu Sans", 25)   #   monospace font
        
        self.update_colours()

        self.quit_symbol_rect: pg.Rect = self.quit_symbol.get_rect(center = self.quit_button.center)
        self.min_symbol_rect: pg.Rect = self.min_symbol.get_rect(center = self.min_button.center)
        
        
        #   hover identifier
        self.hover_button = None
        
    def update_colours(self) -> None:
        
        #   update colours
        self.base_colour = self.settings.theme.background
        self.quit_hover_colour = (255, 0, 0)    #   red
        self.min_hover_button = self.settings.theme.hover
        
        self.quit_symbol: pg.Surface = self.font.render("x", True, self.settings.theme.main)
        self.min_symbol: pg.Surface = self.font.render("_", True, self.settings.theme.main)
    
    def update(self) -> None:
        self.update_colours()        
        
    def handle_button_hovered(self, mouse_pos: tuple) -> None:
        
        old_hover = self.hover_button
        
        if self.quit_button.collidepoint(mouse_pos):
            self.hover_button = "quit"
        
        elif self.min_button.collidepoint(mouse_pos):
            self.hover_button = "minimise"
            
        else:
            self.hover_button = None
        
        if old_hover != self.hover_button:
            logger.debug(f"Hovering {self.hover_button}")
    
    def handle_button_clicked(self, mouse_pos: tuple) -> str | None:
        
        if self.quit_button.collidepoint(mouse_pos):
            logger.info("Clicked quit button")
            return "quit"
        
        elif self.min_button.collidepoint(mouse_pos):
            logger.info("Clicked minimise button")
            return "minimise"
        
        return
        
    def handle_events(self, event: pg.event.Event) -> str | None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        #   if mouse movement is detected
        if event.type == pg.MOUSEMOTION:
            self.handle_button_hovered(mouse_pos)
        
        #   if left button is pressed
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            return self.handle_button_clicked(mouse_pos)

        return   
    
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   set button colour
        quit_colour: tuple = self.quit_hover_colour if self.hover_button == "quit" else self.base_colour
        min_colour: tuple = self.min_hover_button if self.hover_button == "minimise" else self.base_colour
        
        #   draw buttons
        pg.draw.rect(screen, quit_colour, self.quit_button)
        pg.draw.rect(screen, min_colour, self.min_button)
    
        #   draw symbols
        screen.blit(self.quit_symbol, self.quit_symbol_rect)
        screen.blit(self.min_symbol, self.min_symbol_rect)
        
        #   draw line
        pg.draw.line(screen, self.settings.theme.main, (0, self.button_height), (self.screen_width, self.button_height), 3)