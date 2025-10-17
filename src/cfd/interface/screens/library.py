import pygame as pg

import logging

from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import NULLWIDGET, Widget, RectButton, ProjectButton
from cfd.utilities.files_manager import scan_projects

logger = logging.getLogger(__name__)


class LibraryScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)
        
        self.btn_dim = (0.15 * config.width, 0.04 * config.height)
        
        #   ==========[ BUTTONS ]==========
        self.create_btn = RectButton(name="crt_proj_btn", rect=pg.Rect(self._get_grid(0, 1), self.btn_dim), text="Create Project")
        
        #   ==========[ PROJECT ENTRIES ]==========
        projects = scan_projects()        
        
        self.buttons: list[RectButton] = [
            self.create_btn
        ]
        
        self.hovering: Widget = NULLWIDGET
        
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        """return suitable position for widgets in specific 'row and 'columns'"""
        
        if title: return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else: return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
        
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_button_hovered(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.hovering
        hovered = False

        #   loop through every button and detect collision with mouse pos
        for button in self.buttons:
            if button.collide(mouse_pos):
                self.hovering = button
                hovered = True
                break
        if not hovered: self.hovering = NULLWIDGET
        
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_button_clicked(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.hovering.name: return
        
        event = None
        extra_data = {}
        
        match self.hovering.id:
            
            case self.create_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data["screen_id"] = Screens.CRT_PROJ.value
                
            case _:
                return
        logger.debug(f"Clicked {self.hovering.name}")
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
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)
    
    def update(self) -> None:
        
        self.create_btn.update(self.hovering.id, -1)
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, self.title_pos)
        
        #   draw buttons
        self.create_btn.draw(screen)