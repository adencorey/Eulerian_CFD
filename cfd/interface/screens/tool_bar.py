import pygame as pg

import logging

from cfd.settings.manager import settings
from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import Widget, NULLWIDGET, RectButton, WindowButton, SideBarButton

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
        self.quit_btn = WindowButton(name="quit_btn", rect=pg.Rect(config.width - self.win_btn_width, 0, self.win_btn_width, self.win_btn_height), symbol="x")
        self.min_btn = WindowButton(name="min_btn", rect=pg.Rect(config.width - 2 * self.win_btn_width, 0, self.win_btn_width, self.win_btn_height), symbol="_")
        
        #   ==========[ FPS/TPS LABEL ]==========
        self.fps_lbl_pos = int(0.01 * config.width + self.side_btn_len), int(0.05 * config.height)
        self.tps_lbl_pos = int(0.1 * config.width + self.side_btn_len), int(0.05 * config.height)
        
        #   ==========[ SIDEBAR BUTTONS ]==========
        self.library_btn = SideBarButton(name="lib_scn_btn", rect=pg.Rect(0, self.win_btn_height + self.side_btn_len, self.side_btn_len, self.side_btn_len), image="library.png")
        self.settings_btn = SideBarButton(name="settings_scn_btn", rect=pg.Rect(0, config.height - self.side_btn_len, self.side_btn_len, self.side_btn_len), image="settings.png")
        
        self.buttons: list[WindowButton | RectButton | SideBarButton] = [
            self.quit_btn,
            self.min_btn,
            self.library_btn,
            self.settings_btn
        ]
        
        self.hovering:Widget = NULLWIDGET
        self.highlight:Widget = self.library_btn

        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_button_hovered(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.hovering
        hovered = False

        #   loop through every button and detect collision with mouse pos
        for button in self.buttons:
            if button.collide(mouse_pos):
                self.hovering = button
                hovered = True
                break
        if not hovered: self.hovering = NULLWIDGET
        
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_button_clicked(self) -> str | None:
        """calls function if a button is clicked"""
        
        if not self.hovering.name: return
        
        event = None
        extra_data = {}
        
        match self.hovering.id:
            
            case self.highlight.id:
                return
            
            case self.quit_btn.id:
                event = Events.QUIT_PROGRAM
                
            case self.min_btn.id:
                pg.display.iconify()
                
            case self.library_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data["screen_id"] = Screens.LIBRARY.value
                self.highlight = self.library_btn
                
            case self.settings_btn.id:
                event = Events.SCREEN_SWITCH
                extra_data["screen_id"] = Screens.SETTINGS.value
                self.highlight = self.settings_btn
            case _:
                return
            
        logger.debug(f"Clicked {self.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_button_hovered(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_button_clicked()
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self, fps, tps) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["sub"].render("Eulerian CFD", True, config.main_clr)
        if settings.show_fps: self.fps_lbl_surf = config.font["sub"].render(f"FPS: {fps:.2f}", True, config.main_clr)
        if settings.show_tps: self.tps_lbl_surf = config.font["sub"].render(f"TPS: {tps:.2f}", True, config.main_clr)
    
    def update(self, fps:float, tps:float) -> None:
        
        self._update_text(fps, tps)
        for button in self.buttons:
            button.update(self.hovering.id, self.highlight.id)
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw tool bar background
        pg.draw.rect(screen, config.bg_clr, (0, 0, config.width, self.win_btn_height))
        pg.draw.rect(screen, config.bg_clr, (0, 0, self.side_btn_len, config.height))
        
        #   draw title
        screen.blit(self.title_surf, self.title_rect)
        
        #   draw fps/tps
        if settings.show_fps: screen.blit(self.fps_lbl_surf, self.fps_lbl_pos)
        if settings.show_tps: screen.blit(self.tps_lbl_surf, self.tps_lbl_pos)
        
        #   draw buttons
        for button in self.buttons:
            button.draw(screen)