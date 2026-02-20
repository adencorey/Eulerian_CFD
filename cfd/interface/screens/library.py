import pygame as pg

import logging
from itertools import chain

from cfd.helpers.time import get_now
from cfd.interface.config import Events, Screens, Delay, config
from cfd.interface.widgets import NULLWIDGET, Widget, Info, RectButton, ProjectButton
from cfd.helpers.files import scan_projects, delete_project, edit_project
from cfd.helpers.screen import get_grid, TITLE_POS

logger = logging.getLogger(__name__)


class LibraryScreen:
    
    def __init__(self, app) -> None:
        from cfd.app import App
        self.app: App = app
        
        self.title_surf = config.font["title"].render("Library", True, config.main_clr)        
        self.btn_dim = (int(0.2 * config.width), int(0.05 * config.height))
        self.proj_dim = (int(0.5 * config.width), int(0.1 * config.height))
        
        #   ==========[ BUTTONS ]==========
        self.load_btn = RectButton(name="load_proj_btn", rect=pg.Rect(get_grid(3, 10), self.btn_dim), text="Load Project", disabled=True)
        self.crt_btn = RectButton(name="crt_proj_scn_btn", rect=pg.Rect(get_grid(3, 13), self.btn_dim), text="Create Project")
        self.edit_btn = RectButton(name="edit_proj_scn_btn", rect=pg.Rect(get_grid(3, 16), self.btn_dim), text="Edit Project", disabled=True)
        self.del_btn = RectButton(name="del_proj_btn", rect=pg.Rect(get_grid(3, 19), self.btn_dim), text="Delete Project", disabled=True)
        self.alter_buttons: list[RectButton] = [self.load_btn, self.edit_btn, self.del_btn]

        #   ==========[ PROJECT ENTRIES ]==========        
        project_entries = scan_projects()
        self.projects: list[ProjectButton] = []
        col = 7
        for project in project_entries:
            widget_name = f"{project.name.replace(' ', '-')}_proj_btn"
            self.projects.append(ProjectButton(name=widget_name, rect=pg.Rect(get_grid(12, col), self.proj_dim), project=project))
            col += 4
        
        #   ==========[ PROJECT COUNT LABEL ]==========
        num_proj = len(self.projects)
        self.proj_count_info = Info(name="proj_count_info", title=f"Project count ({num_proj}/5)", pos=get_grid(3, 8), description="Number of projects created, maximum 5 entries.")
        if num_proj == 5: self.crt_btn.disabled = True
        
        self.buttons: list[RectButton | ProjectButton] = [self.crt_btn] + self.alter_buttons + self.projects
        self.infos: list[Info] = [self.proj_count_info]
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.app.hovering
        hovered = NULLWIDGET
        for widget in chain(self.buttons, self.infos):
            if widget.collide(mouse_pos):
                hovered = widget
                break
            
        self.app.hovering = hovered        
        if hovering != self.app.hovering:
            logger.debug(f"Hovering {self.app.hovering.name}")
    
    def _handle_click(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.app.hovering.name:
            self.app.highlighted = NULLWIDGET
            return
        event = None
        extra_data = {}
        
        if isinstance(self.app.hovering, ProjectButton):
            if not self.app.hovering.double_click:
                self.app.highlighted = self.app.hovering
                self.app.project = self.app.hovering.project
                event = Events.DELAY_FUNCTION
                extra_data["function"] = self.app.hovering.toggle_double_click()
                for button in self.alter_buttons:
                    button.disabled = False
                                    
            else:
                event = Events.SCREEN_SWITCH
                extra_data["screen_id"] = Screens.SIMULATION.value
                self.app.highlighted = NULLWIDGET
                self.app.project.metadata["last_opened"] = get_now(False)
                edit_project(self.app.project.name, metadata=self.app.project.metadata)

        else:
            match self.app.hovering.id:
                
                case self.load_btn.id:
                    if not self.load_btn.disabled:
                        event = Events.SCREEN_SWITCH
                        extra_data["screen_id"] = Screens.SIMULATION.value
                        self.app.highlighted = NULLWIDGET
                        self.app.project.metadata["last_opened"] = get_now(False)
                        edit_project(self.app.project.name, metadata=self.app.project.metadata)  
                
                case self.crt_btn.id:
                    if not self.crt_btn.disabled:
                        event = Events.SCREEN_SWITCH
                        extra_data["screen_id"] = Screens.CRT_PROJ.value
                        self.app.highlighted = NULLWIDGET
                
                case self.edit_btn.id:
                    if not self.edit_btn.disabled:
                        event = Events.SCREEN_SWITCH
                        extra_data["screen_id"] = Screens.EDIT_PROJ.value
                        self.app.highlighted = NULLWIDGET
                
                case self.del_btn.id:
                    if not self.del_btn.disabled:
                        if not self.del_btn.confirm:
                            event = Events.DELAY_FUNCTION
                            extra_data["function"] = self.del_btn.toggle_confirm()
                        else:
                            if self.app.highlighted.id:
                                delete_project(self.app.project.name)
                                self.__init__(self.app)
                    
                case _:
                    return
            
        logger.debug(f"Clicked {self.app.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_click()
            

    #   ==========[ UPDATE ]==========
    def update(self) -> None:
        for widget in chain(self.buttons, self.infos):
            widget.update(self.app.hovering.id, self.app.highlighted.id)
        if not self.app.highlighted.id:
            for button in self.alter_buttons: 
                button.disabled = True
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, TITLE_POS)
        
        #   draw buttons
        for widget in chain(self.buttons, self.infos):
            widget.draw(screen)
        for info in self.infos:
            if self.app.hovering.id == info.id:
                info.draw_description(screen)