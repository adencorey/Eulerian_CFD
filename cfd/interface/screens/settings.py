import pygame as pg

import logging
from itertools import chain

from cfd.settings.manager import settings
from cfd.interface.config import config
from cfd.interface.widgets import Widget, Info, NULLWIDGET, Dropdown
from cfd.utilities.screen_helper import get_grid, TITLE_POS

logger = logging.getLogger(__name__)


class SettingsScreen:
    
    def __init__(self) -> None:
        
        self.drp_size = int(0.2 * config.width), int(0.05 * config.height)
        
        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.title_pos = TITLE_POS
        
        #   ==========[ THEME SETTING ]==========
        self.theme_info = Info(name="theme_info", title="Theme", pos=get_grid(3, 7), description="Colour scheme of the program.")
        self.theme_drp = Dropdown(name="theme_drp", rect=pg.Rect(get_grid(3, 8), self.drp_size), options=["light", "dark"], setting=settings.theme_name)

        #   ==========[ FPS SETTING ]==========
        self.fps_info = Info(name="fps_info", title="Frame Rate", pos=get_grid(3, 15), description="Frame per second of the program.")
        self.fps_drp = Dropdown(name="fps_drp", rect=pg.Rect(get_grid(3, 16), self.drp_size), options=["30", "60", "120"], setting=settings.fps)
        
        #   ==========[ SHOW FPS SETTING ]==========
        self.shw_fps_info = Info(name="shw_fps_info", title="Show FPS", pos=get_grid(3, 17), description="Display frame rate on screen.")
        self.shw_fps_drp = Dropdown(name="shw_fps_drp", rect=pg.Rect(get_grid(3, 18), self.drp_size), options=["true", "false"], setting=settings.show_fps)
        
        self.dropdowns:list[Dropdown] = [self.theme_drp, self.fps_drp, self.shw_fps_drp]
        self.infos: list[Info] = [self.theme_info, self.fps_info, self.shw_fps_info]
        self.hovering: Widget = NULLWIDGET
        
    
    #   ==========[ HANDLE EVENTS ]==========    
    def _handle_hover(self, mouse_pos:tuple) -> None:
        """checks if mouse is colliding with a dropdown menus"""
        
        hovering = self.hovering
        hovered = NULLWIDGET
        
        for widget in chain(self.dropdowns, self.infos):
            if widget.collide(mouse_pos):
                hovered = widget
                break
            if isinstance(widget, Dropdown):
                if widget.collide_children(mouse_pos):
                    hovered = widget.hovering
                    break

        self.hovering = hovered
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")

    def _handle_click(self) -> None:
        """calls function if a dropdown menu is clicked"""
        
        #   if any open dropdown not being hovered close it
        for dropdown in self.dropdowns:
            if dropdown.show and self.hovering.id != dropdown.id: dropdown.show = False
        if not self.hovering.name: return
        
        event = None
        extra_data = {}
        clicked = False
        
        if isinstance(self.hovering, Dropdown):
            self.hovering.show = False if self.hovering.show else True
            clicked = True
        
        #   check if hvr_id any menu buttons
        if not clicked:
            
            if self.theme_drp.hovering.name:
                settings.theme_name = self.theme_drp.hovering.text.lower()
                self.theme_drp.clicked(settings.theme_name)
                
            elif self.fps_drp.hovering.name:
                settings.fps = int(self.fps_drp.hovering.text.lower())
                self.fps_drp.clicked(settings.fps)
            
            elif self.shw_fps_drp.hovering.name:
                settings.show_fps = self.shw_fps_drp.hovering.text.lower() == "true"
                self.shw_fps_drp.clicked(settings.show_fps)
            
            #   change settings accordingly
            settings.save()
            config.update()
            
        logger.debug(f"Clicked {self.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:

        mouse_pos:tuple = pg.mouse.get_pos()
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_click()
            
            
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
    
    def update(self, dt) -> None:
        
        for widget in chain(self.dropdowns, self.infos):
            widget.update(self.hovering.id, -1)
        self._update_text()
    
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_pos)    #   title
        
        for widget in chain(self.infos, self.dropdowns):
            if isinstance(widget, Dropdown):
                widget.draw_parent(screen)
                continue
            widget.draw(screen)
            
        for dropdown in self.dropdowns:
            if dropdown.show:
                dropdown.draw_children(screen)
                break                

        for info in self.infos:
            if self.hovering.id == info.id:
                info.draw_description(screen)
                break