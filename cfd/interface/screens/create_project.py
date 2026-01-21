import pygame as pg

import logging
from itertools import chain

from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import Widget, NULLWIDGET, Info, RectButton, TextBox, Slidebar
from cfd.helpers.files import create_project
from cfd.helpers.screen import get_grid, TITLE_POS

logger = logging.getLogger(__name__)

class CreateProjectScreen:
    
    def __init__(self, app) -> None:
        from cfd.app import App
        self.app: App = app
        
        btn_size = int(0.2 * config.width), int(0.05 * config.height)
        tb_size = int(0.35 * config.width), int(0.06 * config.height)
        sb_size = int(0.25 * config.width), int(0.01 * config.height)

        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("Create Project", True, config.main_clr)
        
        #   ==========[ PROJECT NAME ]==========
        self.proj_name_info = Info(name="proj_name_info", title="Project Name", pos=get_grid(10, 5), description="")
        self.proj_textbox = TextBox(name="proj_nme_tbx", rect=pg.Rect(get_grid(15, 7), tb_size), anchor="n", placeholder="New Project", max=30)
        
        #   ==========[ RESOLUTION ]==========
        self.res_info = Info(name="res_info", title="Environment Resolution", pos=get_grid(10, 10), description="Number of cells on either side of the fluid environment (since it is a square). You cannot change this after creating the environment. High performance load.")
        self.res_sb = Slidebar(name="res_sb", rect=pg.Rect(get_grid(15, 12), sb_size), min_val=32, max_val=256, step=4, default=64)
        
        #   ==========[ GRAVITY STRENGTH SLIDEBAR ]==========
        self.grav_info = Info(name="grav_info", title="Gravity Strength", pos=get_grid(10, 15), description="Gravity strength of project environment, multiplier of acceleration due to gravity on Earth (9.81 ms^-2).")
        self.grav_sb = Slidebar(name="grav_sb", rect=pg.Rect(get_grid(15, 17), sb_size), min_val=-1, max_val=5, step=0.1, default=1)
        
        #   ==========[ BACK BUTTON ]==========
        self.canc_btn = RectButton(name="canc_btn", rect=pg.Rect(get_grid(10, 25), btn_size), anchor="n", text="Cancel")
        
        #   ==========[ CREATE BUTTON ]==========
        self.crt_btn = RectButton(name="crt_proj_btn", rect=pg.Rect(get_grid(20, 25), btn_size), anchor="n", text="Create Project")
        
        
        self.buttons: list[RectButton] = [self.canc_btn, self.crt_btn]
        self.textboxes: list[TextBox] = [self.proj_textbox]
        self.slidebars: list[Slidebar] = [self.res_sb, self.grav_sb]
        self.infos: list[Info] = [self.proj_name_info, self.res_info, self.grav_info]
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.app.hovering
        hovered = NULLWIDGET

        for widget in chain(self.buttons, self.textboxes, self.slidebars, self.infos):
            if widget.collide(mouse_pos):
                hovered = widget
                break
            
        self.app.hovering = hovered
        if hovering != self.app.hovering:
            logger.debug(f"Hovering {self.app.hovering.name}")
    
    def _handle_click(self) -> None:
        """calls function if a button is clicked"""
        
        #   unselect all textboxes
        for textbox in self.textboxes:
            if textbox.selected: 
                textbox.selected = False
        self.app.selected = NULLWIDGET
        if not self.app.hovering.id: return
        
        event = None
        extra_data = {}
        clicked = False
        
        for widget in chain(self.textboxes, self.slidebars):
            if self.app.hovering.id == widget.id:
                if isinstance(widget, TextBox):
                    widget.selected = True
                    self.app.selected = widget
                elif isinstance(widget, Slidebar):
                    widget.dragging = True
                clicked = True
                break
            
        if not clicked:
            match self.app.hovering.id:
                
                case self.canc_btn.id:
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.LIBRARY.value
                    
                case self.crt_btn.id:
                    create_project(self.proj_textbox.get_input(), int(self.res_sb.value), self.grav_sb.value)
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.LIBRARY.value
            
        logger.debug(f"Clicked {self.app.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def _handle_drag(self, mouse_pos) -> None:
        
        for slidebar in self.slidebars:
            if slidebar.dragging:
                slidebar.x_pos = mouse_pos[0]
                break
        
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse = pg.mouse
        mouse_pos = mouse.get_pos()
        left = mouse.get_pressed()[0]
        
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
            if left: self._handle_drag(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and left:
            self._handle_click()
        if event.type == pg.MOUSEBUTTONUP and not left:
            for sb in self.slidebars:
                if sb.dragging: sb.dragging = False
            
        if self.app.selected.id:
            pg.event.post(pg.event.Event(Events.KEYBOARD_INPUT, {"max_char": self.app.selected.max}))
    
    
    #   ==========[ UPDATE ]==========    
    def update(self) -> None:
        for widget in chain(self.buttons, self.textboxes, self.slidebars, self.infos):
            widget.update(self.app.hovering.id, -1)
        if self.app.selected: self.app.selected.text = self.app
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, TITLE_POS)
        
        #   draw widets
        for widget in chain(self.buttons, self.textboxes, self.slidebars, self.infos):
            widget.draw(screen)
        for info in self.infos:
            if self.app.hovering.id == info.id:
                info.draw_description(screen)
                break