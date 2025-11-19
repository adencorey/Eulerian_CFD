import pygame as pg

import logging
from itertools import chain

from cfd.interface.config import Events, Screens, Delay, config
from cfd.interface.widgets import NULLWIDGET, Widget, Info, RectButton, ProjectButton
from cfd.utilities.files_manager import scan_projects, delete_project
from cfd.utilities.screen_helper import get_grid, TITLE_POS

logger = logging.getLogger(__name__)


class LibraryScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)        
        self.btn_dim = (int(0.2 * config.width), int(0.05 * config.height))
        self.proj_dim = (int(0.5 * config.width), int(0.1 * config.height))
        
        #   ==========[ BUTTONS ]==========
        self.crt_btn = RectButton(name="crt_proj_scn_btn", rect=pg.Rect(get_grid(3, 10), self.btn_dim), text="Create Project")
        self.edit_btn = RectButton(name="edit_proj_scn_btn", rect=pg.Rect(get_grid(3, 15), self.btn_dim), text="Edit Project", disabled=True)
        self.del_btn = RectButton(name="del_proj_btn", rect=pg.Rect(get_grid(3, 20), self.btn_dim), text="Delete Project", disabled=True)
        self.alter_buttons: list[RectButton] = [self.edit_btn, self.del_btn]
        
        #   ==========[ PROJECT ENTRIES ]==========        
        project_entries = scan_projects()
        self.projects: list[ProjectButton] = []
        col = 7
        for project in project_entries:
            name, _, metadata = project.values()
            widget_name = f"{name.replace(' ', '-')}_proj_btn"
            self.projects.append(ProjectButton(name=widget_name, rect=pg.Rect(get_grid(12, col), self.proj_dim), text=name, metadata=metadata))
            col += 4
        
        #   ==========[ PROJECT COUNT LABEL ]==========
        num_proj = len(self.projects)
        self.proj_count_info = Info(name="proj_count_info", title=f"Project count ({num_proj}/5)", pos=get_grid(3, 8), description="Number of projects created, maximum 5 entries.")
        if num_proj == 5: self.crt_btn.disabled = True
        
        self.buttons: list[RectButton | ProjectButton] = [self.crt_btn] + self.alter_buttons + self.projects
        self.infos: list[Info] = [self.proj_count_info]
        self.hovering: Widget = NULLWIDGET
        self.highlighting: Widget = NULLWIDGET
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.hovering
        hovered = NULLWIDGET
        for widget in chain(self.buttons, self.infos):
            if widget.collide(mouse_pos):
                hovered = widget
                break
            
        self.hovering = hovered        
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_click(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.hovering.name:
            self.highlighting = NULLWIDGET
            return
        event = None
        extra_data = {}
        clicked = False
        
        for project in self.projects:
            if self.hovering.id == project.id:
                
                if not project.double_click:
                    self.highlighting = project
                    event = Events.DELAY_FUNCTION
                    extra_data["function"] = project.toggle_double_click()
                    for button in self.alter_buttons:
                        button.disabled = False
                                    
                else:
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.SIMULATION.value
                    
                clicked = True
                break
        
        if not clicked:
            match self.hovering.id:
                
                case self.crt_btn.id:
                    if not self.crt_btn.disabled:
                        event = Events.SCREEN_SWITCH
                        extra_data["screen_id"] = Screens.CRT_PROJ.value
                
                case self.edit_btn.id:
                    if not self.edit_btn.disabled:
                        event = Events.SCREEN_SWITCH
                        extra_data["screen_id"] = Screens.EDIT_PROJ.value
                        extra_data["highlighting"] = self.highlighting
                
                case self.del_btn.id:
                    if not self.del_btn.disabled:
                        if not self.del_btn.confirm:
                            event = Events.DELAY_FUNCTION
                            extra_data["function"] = self.del_btn.toggle_confirm()
                        else:
                            if self.highlighting.id:
                                delete_project(self.highlighting.text)
                                self.__init__()
                    
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
    def update(self, dt) -> None:
        for widget in chain(self.buttons, self.infos):
            widget.update(self.hovering.id, self.highlighting.id)
        if not self.highlighting.id:
            for button in self.alter_buttons: 
                button.disabled = True
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, TITLE_POS)
        
        #   draw buttons
        for widget in chain(self.buttons, self.infos):
            widget.draw(screen)
        for info in self.infos:
            if self.hovering.id == info.id:
                info.draw_description(screen)