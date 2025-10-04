import pygame as pg

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import AppWidgets, Widget, NULLWIDGET, config
from fluid_sim.interface.widgets import Dropdown

logger = logging.getLogger(__name__)


class SettingsScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)
        
        self.dropdown_size = int(0.2 * config.width), int(0.05 * config.height)
        
        #   ==========[ THEME SETTING ]==========
        self.theme_title_surf = config.font["head"].render("Theme", True, config.main_clr)
        self.theme_title_pos = self._get_grid(0, 1, title=True)
        self.theme_dropdown = Dropdown(info=AppWidgets.THEME_DROP, rect=pg.Rect(self._get_grid(0, 1), self.dropdown_size), options=["light", "dark"], setting=settings.theme_name)

        #   ==========[ FPS SETTING ]==========
        self.fps_title_surf = config.font["head"].render("Frame Rate", True, config.main_clr)
        self.fps_title_pos = self._get_grid(0, 3, title=True)
        self.fps_dropdown = Dropdown(info=AppWidgets.FPS_DROP, rect=pg.Rect(self._get_grid(0, 3), self.dropdown_size), options=["30", "45", "60", "120"], setting=settings.fps)
        
        #   ==========[ SHOW FPS SETTING ]==========
        self.show_fps_title_surf = config.font["head"].render("Show FPS", True, config.main_clr)
        self.show_fps_title_pos = self._get_grid(0, 4, title=True)
        self.show_fps_dropdown = Dropdown(info=AppWidgets.SHOW_FPS_DROP, rect=pg.Rect(self._get_grid(0, 4), self.dropdown_size), options=["true", "false"], setting=settings.show_fps)
        
        self.dropdowns:list[list[Dropdown]] = [
            [self.theme_title_surf, self.theme_title_pos, self.theme_dropdown],
            [self.fps_title_surf, self.fps_title_pos, self.fps_dropdown],
            [self.show_fps_title_surf, self.show_fps_title_pos, self.show_fps_dropdown]
        ]
        
        self.hovering: Widget = NULLWIDGET
        
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        """return suitable position for widgets in specific 'row and 'columns'"""
        
        if title: return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else: return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
    
    
    #   ==========[ HANDLE EVENTS ]==========    
    def _handle_dropdown_hovered(self, mouse_pos:tuple) -> None:
        """checks if mouse is colliding with a dropdown menus"""
        
        hovering = self.hovering
        hovered = False
        
        #   loop through every dropdown and check collision with mouse pos
        for _, _, dropdown in self.dropdowns:
            #   check collision with main block
            if dropdown.collide(mouse_pos):
                self.hovering = dropdown
                hovered = True
                break
            
            #   check collision with sub blocks
            elif dropdown.collide_sub(mouse_pos):
                self.hovering = dropdown.hovering
                hovered = True
                break
            
        if not hovered: self.hovering = NULLWIDGET
            
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")

    def _handle_dropdown_clicked(self) -> None:
        """calls function if a dropdown menu is clicked"""
        
        #   if any open dropdown not being hovered close it
        for _, _, dropdown in self.dropdowns:
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
            
            if self.theme_dropdown.hovering.name:
                settings.theme_name = self.theme_dropdown.hovering.text.lower()
                self.theme_dropdown.clicked(settings.theme_name)
                
            elif self.fps_dropdown.hovering.name:
                settings.fps = int(self.fps_dropdown.hovering.text.lower())
                self.fps_dropdown.clicked(settings.fps)
            
            elif self.show_fps_dropdown.hovering.name:
                settings.show_fps = self.show_fps_dropdown.hovering.text.lower() == "true"
                self.show_fps_dropdown.clicked(settings.show_fps)
            
            #   change settings accordingly
            settings.save()
            config.update()
            
        logger.debug(f"Clicked {self.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:

        mouse_pos:tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_dropdown_hovered(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_dropdown_clicked()
            
            
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.dropdowns[0][0] = config.font["head"].render("Theme", True, config.main_clr)
        self.dropdowns[1][0] = self.fps_title_surf = config.font["head"].render("Frame Rate", True, config.main_clr)
        self.dropdowns[2][0] = self.show_fps_title_surf = config.font["head"].render("Show FPS", True, config.main_clr)
    
    def update(self) -> None:
        
        for _, _, dropdown in self.dropdowns:
            dropdown.update(self.hovering.id)
        self._update_text()
    
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_pos)    #   title
        
        #   dropdowns
        for surf, pos, dropdown in self.dropdowns:
            screen.blit(surf, pos)
            dropdown.draw_parent(screen)
        
        for _, _, dropdown in self.dropdowns:
            if dropdown.show: dropdown.draw_children(screen)