import pygame as pg

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import config
from fluid_sim.interface.widgets import DropDown

logger = logging.getLogger(__name__)


class SettingsScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)
        
        self.dropdown_size = int(0.2 * config.width), int(0.05 * config.height)
        
        #   ==========[ THEME SETTING ]==========
        self.theme_title_surf = config.font["head"].render("Theme", True, config.main_clr)
        self.theme_title_pos = self._get_grid(0, 1, title=True)
        self.theme_dropdown = DropDown(name="theme-dropdown", rect=pg.Rect(self._get_grid(0, 1), self.dropdown_size), text=["light", "dark"], setting=settings.theme_name)

        #   ==========[ FPS SETTING ]==========
        self.fps_title_surf = config.font["head"].render("Frame Rate", True, config.main_clr)
        self.fps_title_pos = self._get_grid(0, 3, title=True)
        self.fps_dropdown = DropDown(name="fps-dropdown", rect=pg.Rect(self._get_grid(0, 3), self.dropdown_size), text=["30", "45", "60", "120"], setting=settings.fps)
        
        #   ==========[ SHOW FPS SETTING ]==========
        self.show_fps_title_surf = config.font["head"].render("Show FPS", True, config.main_clr)
        self.show_fps_title_pos = self._get_grid(0, 4, title=True)
        self.show_fps_dropdown = DropDown(name="show-fps-dropdown", rect=pg.Rect(self._get_grid(0, 4), self.dropdown_size), text=["true", "false"], setting=settings.show_fps)
        
        self.dropdowns:list[list[pg.Surface, tuple, DropDown]] = [
            [self.theme_title_surf, self.theme_title_pos, self.theme_dropdown],
            [self.fps_title_surf, self.fps_title_pos, self.fps_dropdown],
            [self.show_fps_title_surf, self.show_fps_title_pos, self.show_fps_dropdown]
        ]
        self.hovering = None
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        if title:
            return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else:
            return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
    
    #   ==========[ HANDLE EVENTS ]==========    
    def _handle_dropdown_hovered(self, mouse_pos:tuple) -> None:
        
        old_hover = self.hovering
        
        if self.theme_dropdown.collide(mouse_pos):
            self.hovering = self.theme_dropdown.name
        elif self.theme_dropdown.collide_sub(mouse_pos): self.hovering = f"{self.theme_dropdown.name}.{self.theme_dropdown.hovering}"

        elif self.fps_dropdown.collide(mouse_pos):
            self.hovering = self.fps_dropdown.name
        elif self.fps_dropdown.collide_sub(mouse_pos): self.hovering = f"{self.fps_dropdown.name}.{self.fps_dropdown.hovering}"
        
        elif self.show_fps_dropdown.collide(mouse_pos):
            self.hovering = self.show_fps_dropdown.name
        elif self.show_fps_dropdown.collide_sub(mouse_pos): self.hovering = f"{self.show_fps_dropdown.name}.{self.show_fps_dropdown.hovering}"
                
        else:
            self.hovering = None
            
        if old_hover != self.hovering:
            logger.debug(f"Hovering {self.hovering}")

    def _handle_dropdown_clicked(self) -> None:
        
        if not self.hovering: return
        
        event = None
        extra_data = {}
        flag = False
        
        for _, _, dropdown in self.dropdowns:
            if self.hovering == dropdown.name: 
                dropdown.show = False if dropdown.show else True
                flag = True
                break
        
        if not flag:
            if self.theme_dropdown.hovering: 
                settings.theme_name = self.theme_dropdown.hovering
                self.theme_dropdown.clicked(settings.theme_name)
                
            elif self.fps_dropdown.hovering: 
                settings.fps = int(self.fps_dropdown.hovering)        
                self.fps_dropdown.clicked(settings.fps)
            
            elif self.show_fps_dropdown.hovering:
                settings.show_fps = self.show_fps_dropdown.hovering == "true"
                self.show_fps_dropdown.clicked(settings.show_fps)
            
            settings.save()
            config.update()
            
        logger.debug(f"Clicked {self.hovering}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos:tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_dropdown_hovered(mouse_pos)
        
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_dropdown_clicked()
            
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.dropdowns[0][0] = config.font["head"].render("Theme", True, config.main_clr)
        self.dropdowns[1][0] = self.fps_title_surf = config.font["head"].render("Frame Rate", True, config.main_clr)
        self.dropdowns[2][0] = self.show_fps_title_surf = config.font["head"].render("Show FPS", True, config.main_clr)
    
    def update(self) -> None:
        
        for _, _, dropdown in self.dropdowns:
            dropdown.update(self.hovering)
        self._update_text()
    
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_pos)    #   title
        
        #   dropdowns
        for surf, pos, dropdown in self.dropdowns:
            screen.blit(surf, pos)
            dropdown.draw(screen)
        
        for _, _, dropdown in self.dropdowns:
            dropdown.draw_sub(screen)