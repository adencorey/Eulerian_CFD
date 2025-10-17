import pygame as pg

import logging

from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import Widget, NULLWIDGET, RectButton, TextBox
from cfd.utilities.files_manager import create_project

logger = logging.getLogger(__name__)


class CreateProjectScreen:
    
    def __init__(self) -> None:
        
        self.textbox_size = int(0.3 * config.width), int(0.06 * config.height)
        self.btn_size = int(0.2 * config.width), int(0.05 * config.height)

        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("Create Project", True, config.main_clr)
        self.title_pos = int(0.1 * config.width), int(0.06 * config.height)

        #   ==========[ BACK BUTTON ]==========
        self.back_btn = RectButton(name="bck_btn", rect=pg.Rect(self._get_grid(0, -0.5), (0.1 * config.width, 0.04 * config.height)), text="Back")
        
        #   ==========[ PROJECT NAME ]==========
        self.proj_title_surf = config.font["head"].render("Project Name", True, config.main_clr)
        self.proj_title_pos = self._get_grid(0, 1, title=True)
        self.proj_textbox = TextBox(name="proj_nme_tbx", rect=pg.Rect(self._get_grid(0, 1), self.textbox_size), placeholder="New Project", max=30)
        
        #   ==========[ CREATE BUTTON ]==========
        self.create_btn = RectButton(name="crt_proj_btn", rect=pg.Rect(self._get_grid(0, 3), self.btn_size), text="Create Project")
        
        self.buttons: list[RectButton] = [
            self.back_btn,
            self.create_btn
        ]
        self.textboxes: list[list[TextBox]] = [
            [self.proj_title_surf, self.proj_title_pos, self.proj_textbox]
        ]
        
        self.hovering: Widget = NULLWIDGET
        self.selected: TextBox = NULLWIDGET
        
        
    def _get_grid(self, row, col, title=False) -> tuple[int, int]:
        """return suitable position for widgets in specific 'row and 'columns'"""
        
        if title:
            return int((row * 0.2 + 0.11) * config.width), int((col * 0.05 + 0.08) * config.width)
        else:
            return int((row * 0.2 + 0.1) * config.width), int((col * 0.05 + 0.1) * config.width)
        
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_button_hovered(self, mouse_pos: tuple) -> None:
        """checks if mouse is colliding with a button"""
        
        hovering = self.hovering
        hovered = False

        #   loop through every widget and detect collision with mouse pos
        for button in self.buttons:
            if button.collide(mouse_pos):
                self.hovering = button
                hovered = True
                break
        for _, _, textbox in self.textboxes:
            if textbox.collide(mouse_pos):
                self.hovering = textbox
                hovered = True
                break
            
        if not hovered: self.hovering = NULLWIDGET
        
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_button_clicked(self) -> str | None:
        """calls function if a button is clicked"""
        
        #   unselect all textboxes
        for _, _, textbox in self.textboxes:
            if textbox.selected: textbox.selected = False
        self.selected = NULLWIDGET
        if not self.hovering.id: return
        
        event = None
        extra_data = {}
        clicked = False
        
        for _, _, textbox in self.textboxes:
            if self.hovering.id == textbox.id:
                textbox.selected = True
                self.selected = textbox
                clicked = True
                break
        
        if not clicked:
            match self.hovering.id:
                
                case self.back_btn.id:
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.LIBRARY.value
                    
                case self.create_btn.id:
                    create_project(self.proj_textbox.text, 1)
                    event = Events.SCREEN_SWITCH
                    extra_data["screen_id"] = Screens.LIBRARY.value
                    
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
            
        if self.selected.id:
            pg.event.post(pg.event.Event(Events.KEYBOARD_INPUT, {"max_char": self.selected.max}))
            
    def handle_type(self, text:str) -> None:
        self.selected.text = text
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("None", True, config.main_clr)
    
    def update(self) -> None:
        
        for button in self.buttons:
            button.update(self.hovering.id, None)
        for _, _, textbox in self.textboxes:
            textbox.update()
         
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        #   draw title
        screen.blit(self.title_surf, self.title_pos)
        
        #   draw widets
        for button in self.buttons:
            button.draw(screen)
        for _, _, textbox in self.textboxes:
            textbox.draw(screen)