import pygame as pg

import logging

from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import NULLWIDGET, Widget, RectButton, ProjectButton
from cfd.utilities.files_manager import scan_projects
from cfd.utilities.screen_helper import get_grid, TITLE_POS

logger = logging.getLogger(__name__)


class LibraryScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)        
        self.btn_dim = (int(0.2 * config.width), int(0.05 * config.height))
        self.proj_dim = (int(0.5 * config.width), int(0.1 * config.height))
        
        #   ==========[ BUTTONS ]==========
        self.crt_btn = RectButton(name="crt_proj_scn_btn", rect=pg.Rect(get_grid(3, 8), self.btn_dim), text="Create Project")
        
        #   ==========[ PROJECT ENTRIES ]==========        
        project_entries = scan_projects()
        projects: list[ProjectButton] = []
        col = 7
        for project in project_entries:
            name, _, _, metadata = project.values()
            widget_name = f"{name.replace(' ', '-')}_proj_btn"
            projects.append(ProjectButton(name=widget_name, rect=pg.Rect(get_grid(12, col), self.proj_dim), text=name, metadata=metadata))
            col += 4
        
        self.buttons: list[RectButton | ProjectButton] = [self.crt_btn] + projects
        self.hovering: Widget = NULLWIDGET
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.hovering
        hovered = NULLWIDGET
        for button in self.buttons:
            if button.collide(mouse_pos):
                hovered = button
                break
            
        self.hovering = hovered        
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_click(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.hovering.name: return
        event = None
        extra_data = {}
        
        match self.hovering.id:
            
            case self.crt_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data["screen_id"] = Screens.CRT_PROJ.value
                
            case _:
                return
        logger.debug(f"Clicked {self.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_click()
            

    #   ==========[ UPDATE ]==========
    def _update_text(self, fps) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)
    
    def update(self) -> None:
        
        for button in self.buttons:
            button.update(self.hovering.id, -1)
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, TITLE_POS)
        
        #   draw buttons
        for button in self.buttons:
            button.draw(screen)