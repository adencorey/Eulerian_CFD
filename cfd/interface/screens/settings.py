import pygame as pg

import logging
from itertools import chain

from cfd.settings.manager import settings
from cfd.interface.config import config
from cfd.interface.widgets import Widget, Info, NULLWIDGET, Dropdown, CheckBox, Slidebar
from cfd.helpers.screen import get_grid, TITLE_POS, LARGE_WIDGET, SB_DIM

logger = logging.getLogger(__name__)


class SettingsScreen:
    
    def __init__(self, app) -> None:
        from cfd.app import App
        self.app: App = app
        
        #   ==========[ TITLE ]==========
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
        self.title_pos = TITLE_POS
        
        #   ==========[ THEME SETTING ]==========
        self.theme_info = Info(name="theme_info", title="Theme", pos=get_grid(3, 7), description="Appearance of the program.")
        self.theme_drp = Dropdown(name="theme_drp", rect=pg.Rect(get_grid(3, 8), LARGE_WIDGET), options=["light", "dark"], setting=settings.theme_name)

        #   ==========[ FPS SETTING ]==========
        self.fps_info = Info(name="fps_info", title="Frames Per Second", pos=get_grid(3, 14), description="Refresh rate of program. Higher refresh rate increases the accuracy of the simulation. High performance load")
        self.fps_drp = Dropdown(name="fps_drp", rect=pg.Rect(get_grid(3, 15), LARGE_WIDGET), options=["30", "45", "60", "120", "240"], setting=settings.fps)
        self.shw_fps_chk = CheckBox(name="shw_fps_chk", pos=get_grid(3, 18), text="Show FPS", checked=settings.show_fps)
        
        #   ==========[ GAUSS-SEIDEL ITERATION ]
        self.iter_info = Info(name="iter_info", title="Gauss-Seidel Iteration", pos=get_grid(16, 7), description="Number of times pressure solver iterates per frame, more iterations yield better the approximation. High performance load.")
        self.iter_sb = Slidebar(name="iter_sb", rect=pg.Rect(get_grid(21, 9), SB_DIM), min_val=10, max_val=100, step=1, default=settings.iterator)

        #   ==========[ SUCCESSIVE OVER-RELAXATION WEIGHT ]==========
        self.sor_weight_info = Info(name="sor_weight_info", title="Successive Over-relaxation Weight", pos=get_grid(16, 12), description="Artificial multiplier applied on pressure values after every calculation. Pressure values with same degree of accuracy can be calculated with less Gauss-Seidel iterations, but incorrect pressure values may be calculated. Any value higher than 1.8 is not recommended.")
        self.sor_weight_sb = Slidebar(name="sor_weight_sb", rect=pg.Rect(get_grid(21, 14), SB_DIM), min_val=1, max_val=1.9, step=0.05, default=settings.sor_weight)


        self.dropdowns:list[Dropdown] = [self.theme_drp, self.fps_drp]
        self.infos: list[Info] = [self.theme_info, self.fps_info, self.iter_info, self.sor_weight_info]
        self.checkboxes: list[CheckBox] = [self.shw_fps_chk]
        self.slidebars: list[Slidebar] = [self.iter_sb, self.sor_weight_sb]

    
    def _widgets(self) -> chain[Widget]:
        return chain(self.dropdowns, self.infos, self.checkboxes, self.slidebars)
        
    
    #   ==========[ HANDLE EVENTS ]==========    
    def _handle_hover(self, mouse_pos:tuple) -> None:
        """checks if mouse is colliding with a dropdown menus"""
        
        hovering = self.app.hovering
        hovered = NULLWIDGET
        
        for widget in self._widgets():
            if isinstance(widget, Dropdown):
                if widget.collide_children(mouse_pos):
                    hovered = widget.hovering
                    break
            if widget.collide(mouse_pos):
                hovered = widget
                break

        self.app.hovering = hovered
        if hovering != self.app.hovering:
            logger.debug(f"Hovering {self.app.hovering.name}")

    def _handle_click(self) -> None:
        """calls function if a dropdown menu is clicked"""
            
        #   if any open dropdown not being hovered close it
        for drp in self.dropdowns:
            if self.app.hovering.id != drp.id: drp.show = False
        if not self.app.hovering.name: return      #   skip if NULLWIDGET
        
        event = None
        extra_data = {}
        
        if isinstance(self.app.hovering, Dropdown):
            self.app.hovering.show = not self.app.hovering.show
        elif isinstance(self.app.hovering, Slidebar):
            self.app.hovering.dragging = True
        else:
            if self.app.hovering.id == self.shw_fps_chk.id:
                self.shw_fps_chk.checked = not self.shw_fps_chk.checked
                settings.show_fps = self.shw_fps_chk.checked
                
            elif self.theme_drp.hovering.name:
                settings.theme_name = self.theme_drp.hovering.text.lower()
                self.theme_drp.clicked(settings.theme_name)
                
            elif self.fps_drp.hovering.name:
                settings.fps = int(self.fps_drp.hovering.text)
                self.fps_drp.clicked(settings.fps)
            
            settings.save()
            config.update()
            
        logger.debug(f"Clicked {self.app.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
        
    def _handle_drag(self, mouse_pos) -> None:
        for sb in self.slidebars:
            if sb.dragging:
                sb.x_pos = mouse_pos[0]
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
                if sb.dragging:
                    sb.dragging = False

                    match sb.id:
                        case self.iter_sb.id:
                            settings.iterator = sb.value
                        case self.sor_weight_sb.id:
                            settings.sor_weight = sb.value
                    settings.save()
                    break
            
            
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        """update colour / value of texts"""
        
        self.title_surf = config.font["title"].render("Settings", True, config.main_clr)
    
    def update(self) -> None:
        
        for widget in self._widgets():
            widget.update(self.app.hovering.id, -1)
        self._update_text()
    
    
    #   ==========[ DRAW ]==========
    def draw(self, screen: pg.Surface) -> None:
        
        screen.blit(self.title_surf, self.title_pos)    #   title
        
        for widget in self._widgets():
            if isinstance(widget, Dropdown):
                widget.draw_parent(screen)
                continue
            widget.draw(screen)
            
        for dropdown in self.dropdowns:
            if dropdown.show:
                dropdown.draw_children(screen)
                break                

        for info in self.infos:
            if self.app.hovering.id == info.id:
                info.draw_description(screen)
                break