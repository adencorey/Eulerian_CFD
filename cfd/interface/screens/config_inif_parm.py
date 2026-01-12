import pygame as pg
import numpy as np

import logging
from itertools import chain

from cfd.settings.manager import settings
from cfd.interface.config import config, Events, Screens
from cfd.interface.widgets import Widget, NULLWIDGET, Info, Dropdown, Slidebar, CheckBox, RectButton
from cfd.utilities.screen_helper import TITLE_POS, get_grid
from cfd.simulation.grid import Grid

logger = logging.getLogger(__name__)

class ConfigInitParamScreen:
    
    def __init__(self, app) -> None:
        from cfd.app import App
        self.app: App = app
        
        self.title_surf = config.font["title"].render("Edit Environment", True, config.main_clr)

        self.grid = Grid(self.app.dt)
        
        self.drp_dim = (int(0.1 * config.width), int(0.04 * config.height))
        self.sb_dim = int(0.15 * config.width), int(0.008 * config.height)
        self.btn_dim = (int(0.1 * config.width), int(0.04 * config.height))
        
        self.brush_size_info = Info(name="brush_size_info", title="Brush Size", pos=get_grid(2, 9), description="Paint brush size.")
        self.brush_size_sb = Slidebar(name="brush_size_sb", rect=pg.Rect(get_grid(9, 9), self.sb_dim), min_val=0.5, max_val=5, step=0.1, default=2)
        
        self.save_env_btn = RectButton(name="save-env-btn", rect=pg.Rect(get_grid(3, 20), self.btn_dim), text="Save Changes")
        self.cancel_env_btn = RectButton(name="cancel-env-btn", rect=pg.Rect(get_grid(6, 20), self.btn_dim), text="Cancel")
        
        self.infos: list[Info] = [self.brush_size_info]
        self.drps: list[Dropdown] = []
        self.sbs: list[Slidebar] = [self.brush_size_sb]
        self.chks: list[CheckBox] = []
        self.btns: list[RectButton] = [self.save_env_btn, self.cancel_env_btn]
        
        self.hover_idx: tuple[int, int] = None
        
        self.base_img = np.zeros([self.grid.num_cells, self.grid.num_cells, 3], dtype=np.uint8)
        self.vel_img = np.zeros((self.grid.grid_size[1], self.grid.grid_size[0], 3), dtype=np.uint8)
        self.img_surf = pg.surfarray.make_surface(self.vel_img)
        
    def get_widget_chain(self) -> chain[Widget]:
        return chain(self.drps, self.infos, self.sbs, self.chks, self.btns)
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:        
        
        hovering = self.app.hovering
        hovered = NULLWIDGET
        
        for widget in self.get_widget_chain():
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
        
        #   if any open dropdown not being hovered close it
        for dropdown in self.drps:
            if dropdown.show and self.app.hovering.id != dropdown.id: dropdown.show = False
        if not self.app.hovering.name: return
        
        event = None
        extra_data = {}
        
        if isinstance(self.app.hovering, Dropdown):
            self.app.hovering.show = False if self.app.hovering.show else True
        
        elif self.app.hovering.id == self.save_env_btn.id:
            event = Events.SCREEN_SWITCH
            extra_data["screen_id"] = Screens.SIMULATION
        
        elif self.app.hovering.id == self.cancel_env_btn.id:
            event = Events.SCREEN_SWITCH
            extra_data["screen_id"] = Screens.SIMULATION
            
        else:
            for widget in self.get_widget_chain():
                if self.app.hovering.id == widget.id:
                    if isinstance(widget, Slidebar):
                        widget.dragging = True
                    elif isinstance(widget, CheckBox):
                        widget.checked = not widget.checked
                    break
        
        logger.debug(f"Clicked {self.app.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
    
    def _handle_drag(self, mouse_pos, mouse_rel, left, mid, right) -> None:
        
        for slidebar in self.sbs:
            if slidebar.dragging:
                slidebar.x_pos = mouse_pos[0]
                break
        
        #   external velocity / smoke density by user
        if self.hover_idx:
            i, j = self.hover_idx
            radius = int(self.grid.scale * self.brush_size_sb.value)
            
            i_start = max(i - radius, 1)
            j_start = max(j - radius, 1)
            i_end = min(i + radius + 1, self.grid.num_cells - 1)
            j_end = min(j + radius + 1, self.grid.num_cells - 1)
            
            #   create weight matrix to create smooth decrease from center
            x_span = np.arange(i_start, i_end)
            y_span = np.arange(j_start, j_end)
            x, y = np.meshgrid(x_span, y_span, indexing='ij')
            weight: np.ndarray = 1 - np.hypot(x - i, y - j) / radius
            weight = np.clip(weight, 0, 1)
            
            if left:
                rx, ry = mouse_rel                                                                  #   velocity in pixel/tick
                px_to_m_scale = self.grid.cell_size / self.grid.cell_px                             #   convertion scalar from pixel to meter, unit: meter/pixel
                self.grid.u[i_start:i_end, j_start:j_end] += rx * px_to_m_scale / self.app.dt * weight  #   convert to ms-1: pixel * (meter/pixel) / second = meter/second
                self.grid.v[i_start:i_end, j_start:j_end] -= ry * px_to_m_scale / self.app.dt * weight
            
            if mid:
                self.grid.w[i_start:i_end, j_start:j_end] = 1 - np.clip((weight * 2 * radius).astype(np.uint8), 0, 1)
                
            if right:
                self.grid.s[i_start:i_end, j_start:j_end] += weight
                np.clip(self.grid.s, 0, 1, out=self.grid.s)
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        mouse = pg.mouse
        mouse_pos = mouse.get_pos()
        mouse_rel = mouse.get_rel()
        left, mid, right = mouse.get_pressed()
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
            self.hover_idx = self.grid.hovered_cell(mouse_pos)
            self._handle_drag(mouse_pos, mouse_rel, left, mid, right)
        if event.type == pg.MOUSEBUTTONDOWN and mouse.get_pressed()[0]:
            self._handle_click()
        if event.type == pg.MOUSEBUTTONUP and not mouse.get_pressed()[0]:
            self.brush_size_sb.dragging = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.wind_tunnel = not self.wind_tunnel
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        pass
        
        
    def update(self) -> None:
        
        for widget in self.get_widget_chain():
            widget.update(self.app.hovering.id, -1)
        
    def _update_screen(self) -> None:
        self._update_text()        
    
    #   ==========[ DRAW ]==========
    def draw_grid(self, screen:pg.Surface) -> None:
        
        self.grid.get_walls_field_img(self.base_img)
        base_surf = pg.surfarray.make_surface(self.base_img)
        self.img_surf.blit(pg.transform.scale(base_surf, self.grid.grid_size), (0, 0))
        screen.blit(self.img_surf, self.grid.rect)
        
        if np.any(self.vel_img != 0):
            vel_surf = pg.surfarray.make_surface(self.vel_img)
            vel_surf.set_colorkey((0, 0, 0))
            screen.blit(vel_surf, self.grid.rect)
        
        
    def draw(self, screen:pg.Surface) -> None:
        
        screen.blit(self.title_surf, TITLE_POS)     #   draw title
        self.draw_grid(screen)
        
        for widget in self.get_widget_chain():
            if isinstance(widget, Dropdown):
                widget.draw_parent(screen)
                continue
            widget.draw(screen)
            
        for dropdown in self.drps:
            if dropdown.show:
                dropdown.draw_children(screen)
                break                
            
        for info in self.infos:
            if self.app.hovering.id == info.id:
                info.draw_description(screen)
                break