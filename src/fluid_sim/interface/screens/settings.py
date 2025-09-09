import pygame as pg

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import Widget, config
from fluid_sim.interface.widgets import DropDown

logger = logging.getLogger(__name__)


class SettingsScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)
        
        #   ==========[ THEME SETTING ]==========
        self.theme_title_surf = config.font["body"].render("Theme", True, config.main_clr)
        self.theme_title_pos = self._get_grid(0, 1, title=True)
        self.theme_dropdown = DropDown(name="theme-dropdown", rect=pg.Rect(self._get_grid(0, 1), (int(0.2 * config.width), int(0.05 * config.height))), 
                             text=["Light", "Dark"], setting=settings.theme_name)
        
        self.hovering = None
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        if title:
            return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else:
            return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
    
    #   ==========[ HANDLE EVENTS ]==========
    def _handle_dropdown_sub_hovered(self, dropdown: DropDown, mouse_pos:tuple) -> None:
        
        if dropdown.show:
            for i, rect in enumerate(dropdown.sub_rect):
                if rect.collidepoint(mouse_pos):
                    self.hovering = f"{dropdown.name}.{dropdown.text[i].lower()}"
                    return True
        return False
    
    def _handle_dropdown_hovered(self, mouse_pos:tuple) -> None:
        
        old_hover = self.hovering
        
        if self.theme_dropdown.rect.collidepoint(mouse_pos) or self.theme_dropdown.arrow_rect.collidepoint(mouse_pos):
            self.hovering = self.theme_dropdown.name
        
        elif self._handle_dropdown_sub_hovered(self.theme_dropdown, mouse_pos): pass
        
        else:
            self.hovering = None
            
        if old_hover != self.hovering:
            logger.debug(f"Hovering {self.hovering}")
        
    def _handle_dropdown_clicked(self, mouse_pos:tuple) -> None:
        
        clicked_btn = None
        event = None
        extra_data = {}
        change = False
        if self.theme_dropdown.rect.collidepoint(mouse_pos) or self.theme_dropdown.arrow_rect.collidepoint(mouse_pos):
            clicked_btn = self.theme_dropdown.name
            self.theme_dropdown.show = False if self.theme_dropdown.show else True
            
        elif self.theme_dropdown.show:
            for i, rect in enumerate(self.theme_dropdown.sub_rect):
                if rect.collidepoint(mouse_pos):
                    clicked_btn = f"{self.theme_dropdown.name}.{self.theme_dropdown.text[i].lower()}"
                    settings.theme_name = self.theme_dropdown.text[i].lower()
                    self.theme_dropdown.get_index(settings.theme_name)
                    change = True

        else:
            return
        
        if change:
            self.theme_dropdown.show = False
            settings.save()
            config.update()
            
        logger.debug(f"Clicked {clicked_btn} button")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos:tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_dropdown_hovered(mouse_pos)
        
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_dropdown_clicked(mouse_pos)
            
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.theme_title_surf = config.font["main"].render("Theme", True, config.main_clr)
    
    def update(self) -> None:
        
        self.theme_dropdown.update(self.hovering)
    
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_pos)    #   title
        
        #   theme dropdown
        screen.blit(self.theme_title_surf, self.theme_title_pos)
        self.theme_dropdown.draw(screen)