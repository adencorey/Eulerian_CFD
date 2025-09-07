import pygame as pg

import logging

from fluid_sim.ui.constants import AppScreens
from fluid_sim.settings.manager import Settings
from fluid_sim.ui.constants import QUIT_PROGRAM, SCREEN_SWITCH
from fluid_sim.ui.buttons import RectButton, QuitButton, SideBarButton

logger = logging.getLogger(__name__)

class ToolBar:
    
    def __init__(self, settings: Settings, screen_width, screen_height) -> None:
        
        self.settings = settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pg.font.SysFont("DejaVu Sans", 25)
        
        self.win_btn_width = 0.03 * self.screen_width
        self.win_btn_height = 0.02 * self.screen_width
        
        #   ==========[ TITLE ]==========
        self.title: pg.Surface = self.font.render("Eulerian CFD", True, self.settings.theme.main)
        self.title_rect: pg.Rect = self.title.get_rect(center = (self.screen_width // 2, self.win_btn_height // 2))
        
        #   ==========[ WINDOW BUTTONS ]==========
        self.quit_btn = QuitButton(pg.Rect(self.screen_width - self.win_btn_width, 0, self.win_btn_width, self.win_btn_height))
        self.min_btn = RectButton("minimise-button", pg.Rect(self.screen_width - 2 * self.win_btn_width, 0, self.win_btn_width, self.win_btn_height), "_")
        
        #   ==========[ SIDEBAR BUTTONS ]==========
        self.side_btn_len = 0.04 * self.screen_width
        self.library_btn = SideBarButton("library-button", pg.Rect(0, self.win_btn_height + self.side_btn_len, self.side_btn_len, self.side_btn_len), "library.png")
        self.settings_btn = SideBarButton("settings-button", pg.Rect(0, self.screen_height - self.side_btn_len, self.side_btn_len, self.side_btn_len), "settings.png")
        
        #   hover identifier
        self.hovered_btn = None
        
    def update_colours(self) -> None:
        
        self.title: pg.Surface = self.font.render("Eulerian CFD", True, self.settings.theme.main)
    
    def update(self) -> None:
        
        self.update_colours()        
        
    def handle_button_hovered(self, mouse_pos: tuple) -> None:
        
        old_hover = self.hovered_btn
        
        if self.quit_btn.rect.collidepoint(mouse_pos):
            self.hovered_btn = self.quit_btn.name
        
        elif self.min_btn.rect.collidepoint(mouse_pos):
            self.hovered_btn = self.min_btn.name
            
        elif self.library_btn.collide(mouse_pos):
            self.hovered_btn = self.library_btn.name
            
        elif self.settings_btn.collide(mouse_pos):
            self.hovered_btn = self.settings_btn.name
                        
        else:
            self.hovered_btn = None
        
        if old_hover != self.hovered_btn:
            logger.debug(f"Hovering {self.hovered_btn}")
    
    def handle_button_clicked(self, mouse_pos: tuple) -> str | None:
        
        clicked_btn = None
        extra_data = {}
        if self.quit_btn.rect.collidepoint(mouse_pos):
            clicked_btn = self.quit_btn.name
            event = QUIT_PROGRAM
        
        elif self.min_btn.rect.collidepoint(mouse_pos):
            clicked_btn = self.quit_btn.name
            pg.display.iconify()
            
        elif self.library_btn.collide(mouse_pos):
            clicked_btn = self.library_btn.name
            event = SCREEN_SWITCH
            extra_data = {"screen_id": AppScreens.LIBRARY}
        
        elif self.settings_btn.collide(mouse_pos):
            clicked_btn = self.settings_btn.name
            event = SCREEN_SWITCH
            extra_data = {"screen_id": AppScreens.SETTINGS.value}
        
        logger.debug(f"Clicked {clicked_btn} button")
        pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        #   if mouse movement is detected
        if event.type == pg.MOUSEMOTION:
            self.handle_button_hovered(mouse_pos)
        
        #   if left button is pressed
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self.handle_button_clicked(mouse_pos)
    
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw tool bar background
        pg.draw.rect(screen, self.settings.theme.light_bg, (0, 0, self.screen_width, self.win_btn_height))
        pg.draw.rect(screen, self.settings.theme.light_bg, (0, 0, self.side_btn_len, self.screen_height))
        
        #   draw title
        screen.blit(self.title, self.title_rect)
        
        #   draw window buttons
        self.quit_btn.draw(screen, self.settings.theme, self.hovered_btn)
        self.min_btn.draw(screen, self.settings.theme, self.hovered_btn)
        
        #   draw sidebar buttons
        self.library_btn.draw(screen, self.settings.theme, self.hovered_btn)
        self.settings_btn.draw(screen, self.settings.theme, self.hovered_btn)