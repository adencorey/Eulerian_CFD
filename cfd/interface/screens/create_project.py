import pygame as pg

import logging
from itertools import chain

from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import Widget, NULLWIDGET, Info, RectButton, TextBox, Slidebar
from cfd.utilities.files_manager import create_project
from cfd.utilities.screen_helper import get_grid, TITLE_POS

logger = logging.getLogger(__name__)

class CreateProjectScreen:
    
    def __init__(self) -> None:
        
        self.btn_size = int(0.2 * config.width), int(0.05 * config.height)
        self.tb_size = int(0.35 * config.width), int(0.06 * config.height)
        self.sb_size = int(0.25 * config.width), int(0.01 * config.height)

        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("Create Project", True, config.main_clr)
        
        #   ==========[ PROJECT NAME ]==========
        self.proj_name_info = Info(name="proj_name_info", title="Project Name", pos=get_grid(10, 7), description="Name of the new project")
        self.proj_textbox = TextBox(name="proj_nme_tbx", rect=pg.Rect(get_grid(15, 9), self.tb_size), anchor="n", placeholder="New Project", max=30)
        
        #   ==========[ GRAVITY STRENGTH SLIDEBAR ]==========
        self.grav_info = Info(name="grav_info", title="Gravity Strength", pos=get_grid(10, 15), description="Gravity strength of project environment, multiplier of acceleration due to gravity on Earth (9.81 ms^-2).")
        self.grav_sb = Slidebar(name="grav_sb", rect=pg.Rect(get_grid(15, 17), self.sb_size), min_val=-1, max_val=5, step=0.1, default=1)
        
        #   ==========[ BACK BUTTON ]==========
        self.canc_btn = RectButton(name="canc_btn", rect=pg.Rect(get_grid(10, 25), self.btn_size), anchor="n", text="Cancel")
        
        #   ==========[ CREATE BUTTON ]==========
        self.crt_btn = RectButton(name="crt_proj_btn", rect=pg.Rect(get_grid(20, 25), self.btn_size), anchor="n", text="Create Project")
        
        
        self.buttons: list[RectButton] = [self.canc_btn, self.crt_btn]
        self.textboxes: list[TextBox] = [self.proj_textbox]
        self.slidebars: list[Slidebar] = [self.grav_sb]
        self.infos: list[Info] = [self.proj_name_info, self.grav_info]
        
        self.hovering: Widget = NULLWIDGET
        self.selected: TextBox = NULLWIDGET
        
        pg.event.post(pg.event.Event(Events.CLEAR_INPUT, {}))

        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.hovering
        hovered = NULLWIDGET

        for widget in chain(self.buttons, self.textboxes, self.slidebars, self.infos):
            if widget.collide(mouse_pos):
                hovered = widget
                break
            
        self.hovering = hovered
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_click(self) -> None:
        """calls function if a button is clicked"""
        
        #   unselect all textboxes
        for textbox in self.textboxes:
            if textbox.selected: 
                textbox.selected = False
        self.selected = NULLWIDGET
        if not self.hovering.id: return
        
        event = None
        extra_data = {}
        clicked = False
        
        for widget in chain(self.textboxes, self.slidebars):
            if self.hovering.id == widget.id:
                if isinstance(widget, TextBox):
                    widget.selected = True
                    self.selected = widget
                elif isinstance(widget, Slidebar):
                    widget.dragging = True
                clicked = True
                break
            
        if not clicked:
            match self.hovering.id:
                
                case self.canc_btn.id:
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.LIBRARY.value
                    
                case self.crt_btn.id:
                    create_project(self.proj_textbox.text, self.grav_sb.value)
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.LIBRARY.value
            
        logger.debug(f"Clicked {self.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def _handle_drag(self, mouse_pos) -> None:
        
        for slidebar in self.slidebars:
            if slidebar.dragging:
                slidebar.x_pos = mouse_pos[0]
                break
        
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse_pos: tuple = pg.mouse.get_pos()
        
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
        if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
            self._handle_click()
        if pg.mouse.get_pressed()[0]:
            self._handle_drag(mouse_pos)
        if event.type == pg.MOUSEBUTTONUP and not pg.mouse.get_pressed()[0]:
            self.grav_sb.dragging = False
            
        if self.selected.id:
            pg.event.post(pg.event.Event(Events.KEYBOARD_INPUT, {"max_char": self.selected.max}))
            
    def handle_type(self, text:str) -> None:
        self.selected.text = text
    
    
    #   ==========[ UPDATE ]==========    
    def update(self, dt) -> None:
        for widget in chain(self.buttons, self.textboxes, self.slidebars, self.infos):
            widget.update(self.hovering.id, -1)
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, TITLE_POS)
        
        #   draw widets
        for widget in chain(self.buttons, self.textboxes, self.slidebars, self.infos):
            widget.draw(screen)
        for info in self.infos:
            if self.hovering.id == info.id:
                info.draw_description(screen)
                break