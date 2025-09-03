import pygame as pg

import logging

logger = logging.getLogger(__name__)


class ToolBar:
    
    def __init__(self, bg_colour: tuple, screen_width: int) -> None:
        
        self.screen_width = screen_width
        self.button_width = 0.03 * self.screen_width
        self.button_height = 0.02 * self.screen_width
        
        #   ==========[ BUTTONS ]==========
        self.quit_button = pg.Rect(self.screen_width - self.button_width, 0, self.button_width, self.button_height)
        self.min_button = pg.Rect(self.screen_width - 2 * self.button_width, 0, self.button_width, self.button_height)
        
        #   symbols
        self.font = pg.font.Font(None, 36)
        
        self.quit_symbol: pg.Surface = self.font.render("×", True, (255, 255, 255))
        self.quit_symbol_rect: pg.Rect = self.quit_symbol.get_rect(center = self.quit_button.center)
        
        self.min_symbol: pg.Surface = self.font.render("_", True, (255, 255, 255))
        self.min_symbol_rect: pg.Rect = self.min_symbol.get_rect(center = self.min_button.center)
        
        #   colours
        self.base_colour: tuple = bg_colour
        self.quit_hover_colour = (255, 0, 0)    #   red
        self.min_hover_button = (100, 100, 100)     #   dark grey
        
        #   hover identifier
        self.hover_button = None
        
    def button_hovered(self, mouse_pos: tuple) -> None:
        
        old_hover = self.hover_button
        
        if self.quit_button.collidepoint(mouse_pos):
            self.hover_button = "quit"
        
        elif self.min_button.collidepoint(mouse_pos):
            self.hover_button = "minimise"
            
        else:
            self.hover_button = None
        
        if old_hover != self.hover_button:
            logger.debug(f"Hovering {self.hover_button}")
    
    def button_clicked(self, mouse_pos: tuple) -> str | None:
        
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
            self.button_hovered(mouse_pos)
        
        #   if left button is pressed
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            return self.button_clicked(mouse_pos)

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