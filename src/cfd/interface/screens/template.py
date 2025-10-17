import pygame as pg

import logging

from cfd.interface.config import AppWidgets, Events, Widget, config
from cfd.interface.widgets import RectButton

logger = logging.getLogger(__name__)

class ToolBar:
    
    def __init__(self) -> None:

        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("None", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)  
        
        self.widgets: list[Widget] = [
            
        ]
        
        self.hvr_name, self.hvr_id = None, None
        
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_button_hovered(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hvr_name = self.hvr_name
        hovered = False

        #   loop through every button and detect collision with mouse pos
        for widget in self.widgets:
            if widget.collide(mouse_pos):
                self.hvr_name, self.hvr_id = widget.name, widget.id
                hovered = True
                break
        if not hovered: self.hvr_name, self.hvr_id = None, None
        
        if hvr_name != self.hvr_name:
            logger.debug(f"Hovering {self.hvr_name}")
    
    def _handle_button_clicked(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.hvr_name: return
        
        event = None
        extra_data = {}
        
        match self.hvr_id:
            
            case None:
                pass
                
            case _:
                return
            
        logger.debug(f"Clicked {self.hvr_name   }")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_button_hovered(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_button_clicked()
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self, fps) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("None", True, config.main_clr)
    
    def update(self, fps:float) -> None:
        
        self._update_text(fps)
        for widget in self.widgets:
            widget.update(self.hvr_id, self.hl_id)
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, self.title_rect)
        
        #   draw widets
        for widget in self.widgets:
            widget.draw(screen)