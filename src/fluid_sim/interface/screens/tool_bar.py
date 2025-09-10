import pygame as pg

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import AppScreens, Events, Widget, config
from fluid_sim.interface.widgets import RectButton, QuitButton, SideBarButton

logger = logging.getLogger(__name__)

class ToolBar:
    
    def __init__(self) -> None:
        
        self.win_btn_width = 0.03 * config.width
        self.win_btn_height = 0.02 * config.width
        
        #   ==========[ TITLE ]==========
        self.title_surf = config.font["sub"].render("Eulerian CFD", True, config.main_clr)
        self.title_rect = self.title_surf.get_rect(center = (config.width // 2, self.win_btn_height // 2))
        
        #   ==========[ WINDOW BUTTONS ]==========
        self.quit_btn = QuitButton(pg.Rect(config.width - self.win_btn_width, 0, self.win_btn_width, self.win_btn_height))
        self.min_btn = RectButton(name="minimise-button", rect=pg.Rect(config.width - 2 * self.win_btn_width, 0, self.win_btn_width, self.win_btn_height), text="_", font=config.font["sub"])
        
        #   ==========[ FPS LABEL ]==========
        self.fps_lbl_pos = int(0.01 * config.width), int(0.01 * config.height)
        
        #   ==========[ SIDEBAR BUTTONS ]==========
        self.side_btn_len = 0.04 * config.width
        self.library_btn = SideBarButton(name="library-button", rect=pg.Rect(0, self.win_btn_height + self.side_btn_len, self.side_btn_len, self.side_btn_len), image="library.png")
        self.settings_btn = SideBarButton(name="settings-button", rect=pg.Rect(0, config.height - self.side_btn_len, self.side_btn_len, self.side_btn_len), image="settings.png")
        
        #   hover identifier
        self.hovering = None
        
        
    #   ==========[ EVENT HANDLING ]==========
    def __handle_button_hovered(self, mouse_pos: tuple) -> None:
        
        old_hover = self.hovering
        
        if self.quit_btn.rect.collidepoint(mouse_pos): self.hovering = self.quit_btn.name
        elif self.min_btn.rect.collidepoint(mouse_pos): self.hovering = self.min_btn.name
        elif self.library_btn.collide(mouse_pos): self.hovering = self.library_btn.name
        elif self.settings_btn.collide(mouse_pos): self.hovering = self.settings_btn.name       
        else: self.hovering = None
        
        if old_hover != self.hovering:
            logger.debug(f"Hovering {self.hovering}")
    
    def __handle_button_clicked(self, mouse_pos: tuple) -> str | None:
        
        clicked_btn = None
        extra_data = {}
        if self.quit_btn.rect.collidepoint(mouse_pos):
            clicked_btn = self.quit_btn.name
            event = Events.QUIT_PROGRAM
        
        elif self.min_btn.rect.collidepoint(mouse_pos):
            clicked_btn = self.quit_btn.name
            event = None
            pg.display.iconify()
            
        elif self.library_btn.collide(mouse_pos):
            clicked_btn = self.library_btn.name
            event = Events.SCREEN_SWITCH
            extra_data = {"screen_id": AppScreens.LIBRARY}
        
        elif self.settings_btn.collide(mouse_pos):
            clicked_btn = self.settings_btn.name
            event = Events.SCREEN_SWITCH
            extra_data = {"screen_id": AppScreens.SETTINGS.value}
        
        else:
            return
        logger.debug(f"Clicked {clicked_btn} button")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        #   if mouse movement is detected
        if event.type == pg.MOUSEMOTION:
            self.__handle_button_hovered(mouse_pos)
        
        #   if left button is pressed
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self.__handle_button_clicked(mouse_pos)
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self, fps) -> None:
        
        self.title_surf = config.font["sub"].render("Eulerian CFD", True, settings.theme.main)
        if settings.show_fps: self.fps_lbl_surf = config.font["sub"].render(f"FPS: {fps:.2f}", True, config.main_clr)
    
    def update(self, fps) -> None:
        
        self._update_text(fps)
        self.quit_btn.update(self.hovering)
        self.min_btn.update(self.hovering)
        self.library_btn.update(self.hovering)
        self.settings_btn.update(self.hovering)
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw tool bar background
        pg.draw.rect(screen, settings.theme.light_bg, (0, 0, config.width, self.win_btn_height))
        pg.draw.rect(screen, settings.theme.light_bg, (0, 0, self.side_btn_len, config.height))
        
        #   draw title
        screen.blit(self.title_surf, self.title_rect)
        
        #   draw window buttons
        self.quit_btn.draw(screen)
        self.min_btn.draw(screen)
        
        #   draw fps
        if settings.show_fps: screen.blit(self.fps_lbl_surf, self.fps_lbl_pos)
        
        #   draw side bar buttons
        self.library_btn.draw(screen)
        self.settings_btn.draw(screen)