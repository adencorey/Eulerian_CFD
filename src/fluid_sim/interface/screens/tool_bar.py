import pygame as pg

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import AppScreens, AppWidgets, Events, config
from fluid_sim.interface.widgets import RectButton, WindowButton, SideBarButton

logger = logging.getLogger(__name__)

class ToolBar:
    
    def __init__(self) -> None:
        
        self.win_btn_width = 0.03 * config.width
        self.win_btn_height = 0.02 * config.width
        self.side_btn_len = 0.04 * config.width

        #   ==========[ TITLE ]==========
        self.title_surf = config.font["sub"].render("Eulerian CFD", True, config.main_clr)
        self.title_rect = self.title_surf.get_rect(center = (config.width // 2, self.win_btn_height // 2))
        
        #   ==========[ WINDOW BUTTONS ]==========
        self.quit_btn = WindowButton(info=AppWidgets.QUIT_BTN, rect=pg.Rect(config.width - self.win_btn_width, 0, self.win_btn_width, self.win_btn_height), symbol="x")
        self.min_btn = WindowButton(info=AppWidgets.MIN_BTN, rect=pg.Rect(config.width - 2 * self.win_btn_width, 0, self.win_btn_width, self.win_btn_height), symbol="_")
        
        #   ==========[ FPS LABEL ]==========
        self.fps_lbl_pos = int(0.01 * config.width + self.side_btn_len), int(0.01 * config.height)
        
        #   ==========[ SIDEBAR BUTTONS ]==========
        self.library_btn = SideBarButton(info=AppWidgets.LIBRARY_BTN, rect=pg.Rect(0, self.win_btn_height + self.side_btn_len, self.side_btn_len, self.side_btn_len), image="library.png")
        self.settings_btn = SideBarButton(info=AppWidgets.SETTINGS_BTN, rect=pg.Rect(0, config.height - self.side_btn_len, self.side_btn_len, self.side_btn_len), image="settings.png")
        
        self.buttons: list[WindowButton | RectButton | SideBarButton] = [
            self.quit_btn,
            self.min_btn,
            self.library_btn,
            self.settings_btn
        ]
        
        self.hvr_name, self.hvr_id = None, None
        self.hl_id = self.library_btn.id
        
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_button_hovered(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hvr_name = self.hvr_name
        
        if self.quit_btn.rect.collidepoint(mouse_pos):
            self.hvr_name, self.hvr_id = self.quit_btn.name, self.quit_btn.id
            
        elif self.min_btn.rect.collidepoint(mouse_pos): 
            self.hvr_name, self.hvr_id = self.min_btn.name, self.min_btn.id
            
        elif self.library_btn.collide(mouse_pos): 
            self.hvr_name, self.hvr_id = self.library_btn.name, self.library_btn.id
            
        elif self.settings_btn.collide(mouse_pos):
            self.hvr_name, self.hvr_id = self.settings_btn.name, self.settings_btn.id
            
        else: self.hvr_name, self.hvr_id = None, None
        
        if hvr_name != self.hvr_name:
            logger.debug(f"Hovering {self.hvr_name}")
    
    def _handle_button_clicked(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.hvr_name: return
        
        event = None
        extra_data = {}
        
        match self.hvr_id:
            
            case self.quit_btn.id:
                event = Events.QUIT_PROGRAM
                
            case self.min_btn.id:
                pg.display.iconify()
                
            case self.library_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data = {"screen_id": AppScreens.LIBRARY.value}
                self.hl_id = self.library_btn.id
                
            case self.settings_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data = {"screen_id": AppScreens.SETTINGS.value}
                self.hl_id = self.settings_btn.id
            case _:
                return
            
        logger.debug(f"Clicked {self.hvr_name   }")
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
        
        self.title_surf = config.font["sub"].render("Eulerian CFD", True, settings.theme.main)
        if settings.show_fps: self.fps_lbl_surf = config.font["sub"].render(f"FPS: {fps:.2f}", True, config.main_clr)
    
    def update(self, fps:float) -> None:
        
        self._update_text(fps)
        for button in self.buttons:
            button.update(self.hvr_id, self.hl_id)
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw tool bar background
        pg.draw.rect(screen, settings.theme.light_bg, (0, 0, config.width, self.win_btn_height))
        pg.draw.rect(screen, settings.theme.light_bg, (0, 0, self.side_btn_len, config.height))
        
        #   draw title
        screen.blit(self.title_surf, self.title_rect)
        
        #   draw fps
        if settings.show_fps: screen.blit(self.fps_lbl_surf, self.fps_lbl_pos)
        
        #   draw buttons
        for button in self.buttons:
            button.draw(screen)