import pygame as pg

import logging

from fluid_sim.interface.config import AppWidgets, AppScreens, Events, config
from fluid_sim.interface.widgets import RectButton, TextBox

logger = logging.getLogger(__name__)

class CreateProjectScreen:
    
    def __init__(self) -> None:
        
        self.textbox_size = int(0.3 * config.width), int(0.05 * config.height)

        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("Create Project", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)

        #   ==========[ BACK BUTTON ]==========
        self.back_btn = RectButton(info=AppWidgets.BACK_BTN, rect=pg.Rect(self._get_grid(0, -0.5), (0.1 * config.width, 0.04 * config.height)), text="Back")
        
        #   ==========[ PROJECT NAME ]==========
        self.proj_title_surf = config.font["head"].render("Project Name", True, config.main_clr)
        self.proj_title_pos = self._get_grid(0, 1, title=True)
        self.proj_textbox = TextBox(info=AppWidgets.PROJ_NAME_TEXT, rect=pg.Rect(self._get_grid(0, 1), self.textbox_size), placeholder="New Project")
        
        self.buttons: list[RectButton] = [
            self.back_btn
        ]
        self.textboxes: list[list[TextBox]] = [
            [self.proj_title_surf, self.proj_title_pos, self.proj_textbox]
        ]
        
        self.hvr_name, self.hvr_id = None, None
        
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        """return suitable position for widgets in specific 'row and 'columns'"""
        
        if title:
            return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else:
            return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
        
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_button_hovered(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hvr_name = self.hvr_name
        hovered = False

        #   loop through every widget and detect collision with mouse pos
        for button in self.buttons:
            if button.collide(mouse_pos):
                self.hvr_name, self.hvr_id = button.name, button.id
                hovered = True
                break
        for _, _, textbox in self.textboxes:
            if textbox.collide(mouse_pos):
                self.hvr_name, self.hvr_id = textbox.name, textbox.id
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
        
        #   unselect all textboxes
        for _, _, textbox in self.textboxes: 
            if textbox.selected: textbox.selected = False
        
        match self.hvr_id:
            
            case self.back_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data = {"screen_id": AppScreens.LIBRARY.value}
                
            case self.proj_textbox.id:
                self.proj_textbox.selected = True
                
            case _:
                return
            
        logger.debug(f"Clicked {self.hvr_name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_button_hovered(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_button_clicked()
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("None", True, config.main_clr)
    
    def update(self) -> None:
        
        for button in self.buttons:
            button.update(self.hvr_id, None)
        for _, _, textbox in self.textboxes:
            textbox.update(self.hvr_id, None)
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, self.title_pos)
        
        #   draw widets
        for button in self.buttons:
            button.draw(screen)
        for _, _, textbox in self.textboxes:
            textbox.draw(screen)