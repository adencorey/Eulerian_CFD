import pygame as pg
import numpy as np

import logging
from itertools import chain

from cfd.settings.manager import settings
from cfd.interface.config import Events, Screens, config
from cfd.interface.widgets import Widget, NULLWIDGET, Info, RectButton, Dropdown, Slidebar
from cfd.utilities.screen_helper import TITLE_POS, get_grid
from cfd.simulation.grid import Grid

logger = logging.getLogger(__name__)

class SimulationScreen:
    
    def __init__(self) -> None:
        
        self.title_surf = config.font["title"].render("Simulation", True, config.main_clr)
        self.dt = 1 / settings.fps
        self.grid = Grid(self.dt)
        
        self.btn_dim = (int(0.1 * config.width), int(0.04 * config.height))
        self.drp_dim = (int(0.12 * config.width), int(0.04 * config.height))
        self.sb_dim = self.sb_size = int(0.2 * config.width), int(0.01 * config.height)
        
        self.total_div = Info(name="total_div_info", title="Total Divergence: 0", pos=get_grid(3, 6), description="The absolute value of the sum of divergence of the environment")
        self.total_s = Info(name="total_s_info", title="Total Smoke Density: 0", pos=get_grid(3, 7), description="The sum of smoke density of the environment")
        
        self.cell_type = Info(name="cell_type_info", title="Cell Type: -", pos=get_grid(3, 9), description="Cell type, 1 - fluid cell; 0 - wall cell")
        self.cell_idx = Info(name="cell_idx_info", title="Cell Index: (-, -)", pos=get_grid(3, 10), description="Cell index of simulation grid, range from 0 to number of cells - 1")
        self.cell_vel = Info(name="cell_vel_info", title="Velocity: (-, -)", pos=get_grid(3, 11), description="Velocity of cell, in the form (x vel, y vel) in ms^-1")
        self.cell_div = Info(name="cell_div_info", title="Divergence: -", pos=get_grid(3, 12), description="Divergence of cell, inflow if negative else outflow")
        self.cell_s = Info(name="cell_s_info", title="Smoke Density: -", pos=get_grid(3, 13), description="Smoke density of cell, range from 0 to 1")
        self.cell_p = Info(name="cell_p_into", title="Pressure: -", pos=get_grid(3, 14), description="Relative pressure of cell, green if close to zero, red if positive else blue")
        
        self.dsp_field = "Smoke"
        self.dsp_field_info = Info(name="dsp_field_info", title="Display Field", pos=get_grid(3, 16), description="Select type of field to display")
        self.dsp_field_drp = Dropdown(name="dsp_field_drp", rect=pg.Rect(get_grid(8, 16), self.drp_dim), options=["Smoke", "Divergence", "Pressure"], setting=self.dsp_field)
        
        self.shw_vel_info = Info(name="shw_vel_info", title="Show Velocity", pos=get_grid(3, 18), description="Toggle velocity field")
        self.shw_vel_btn = RectButton(name="show_vel_btn", rect=pg.Rect(get_grid(8, 18), self.btn_dim), text="Off")
        
        self.proj_field_info = Info(name="proj_field_info", title="Project Field", pos=get_grid(3, 20), description="Toggle projection step (clears out divergence)")
        self.proj_field_btn = RectButton(name="proj_field_btn", rect=pg.Rect(get_grid(8, 20), self.btn_dim), text="On")
        
        self.advect_field_info = Info(name="advect_field_info", title="Advect Field", pos=get_grid(3, 22), description="Toggle advection step (move velocity and smoke)")
        self.advect_field_btn = RectButton(name="advect_field_btn", rect=pg.Rect(get_grid(8, 22), self.btn_dim), text="On")
        
        self.brush_size_info = Info(name="brush_size_info", title="Brush Size", pos=get_grid(3, 24), description="Scalar for brush radius")
        self.brush_size_sb = Slidebar(name="brush_size_sb", rect=pg.Rect(get_grid(8, 26), self.sb_dim), min_val=0.5, max_val=5, step=0.1, default=1)
        

        self.infos: list[Info] = [self.total_div, self.total_s, self.cell_type, self.cell_idx, self.cell_vel, self.cell_div, self.cell_s, self.cell_p, self.dsp_field_info, self.shw_vel_info, self.proj_field_info, self.advect_field_info, self.brush_size_info]
        self.dropdowns: list[Dropdown] = [self.dsp_field_drp]
        self.btns: list[RectButton] = [self.shw_vel_btn, self.proj_field_btn, self.advect_field_btn]
        self.slidebars: list[Slidebar] = [self.brush_size_sb]
        self.hovering: Widget = NULLWIDGET
        self.hover_idx = None
        
        self.wind_tunnel = False
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:        
        
        hovering = self.hovering
        hovered = NULLWIDGET
        for widget in chain(self.dropdowns, self.infos, self.btns, self.slidebars):
            if isinstance(widget, Dropdown):
                if widget.collide_children(mouse_pos):
                    hovered = widget.hovering
                    break
                
            if widget.collide(mouse_pos):
                hovered = widget
                break
            
        self.hovering = hovered
        if hovering != self.hovering:
            logger.debug(f"Hovering {self.hovering.name}")
    
    def _handle_click(self) -> None:        
        
        #   if any open dropdown not being hovered close it
        for dropdown in self.dropdowns:
            if dropdown.show and self.hovering.id != dropdown.id: dropdown.show = False
        if not self.hovering.name: return
        
        if isinstance(self.hovering, Dropdown):
            self.hovering.show = False if self.hovering.show else True

        elif self.dsp_field_drp.hovering.name:
            self.dsp_field = self.dsp_field_drp.hovering.text
            self.dsp_field_drp.clicked(self.dsp_field)
            
        else:
            clicked = False
            for widget in self.slidebars:
                if self.hovering.id == widget.id:
                    if isinstance(widget, Slidebar):
                        widget.dragging = True
                    clicked = True
                    break
            
            if not clicked:
                match self.hovering.id:
                    case self.shw_vel_btn.id:
                        self.shw_vel_btn.text = "On" if self.shw_vel_btn.text == "Off" else "Off"
                    
                    case self.proj_field_btn.id:
                        self.proj_field_btn.text = "On" if self.proj_field_btn.text == "Off" else "Off"
                        
                    case self.advect_field_btn.id:
                        self.advect_field_btn.text = "On" if self.advect_field_btn.text == "Off" else "Off"
        
        logger.debug(f"Clicked {self.hovering.name}")
    
    def _handle_drag(self, mouse_pos, mouse_rel, left, mid, right) -> None:
        
        for slidebar in self.slidebars:
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
                rx, ry = mouse_rel
                self.grid.u[i_start:i_end, j_start:j_end] += rx / self.dt * weight
                self.grid.v[i_start:i_end, j_start:j_end] -= ry / self.dt * weight
                self.grid.s[i_start:i_end, j_start:j_end] += weight
                np.clip(self.grid.s, 0, 1, out=self.grid.s)
            
            if mid or (left and right):
                self.grid.w[i_start:i_end, j_start:j_end] = 1 - np.clip((weight * 2 * radius).astype(int), 0, 1)
                
            if right:
                pass
        
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
        if event.type == pg.MOUSEBUTTONUP and not pg.mouse.get_pressed()[0]:
            self.brush_size_sb.dragging = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.wind_tunnel = True
        
        if event.type == pg.KEYUP:
            self.wind_tunnel = False
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        self.total_div.title = f"Total Divergence: {np.sum(np.abs(self.grid.div)):.4f}"
        self.total_s.title = f"Total Smoke Density: {np.sum(self.grid.s):.4f}"
        
        if self.hover_idx != None:
            type_text = self.grid.w[self.hover_idx]
            idx_text = self.hover_idx
            vel_text = f"({self.grid.u[self.hover_idx]:.4f}, {self.grid.v[self.hover_idx]:.4f})"
            div_text = f"{self.grid.div[self.hover_idx]:.4f}"
            s_text = f"{self.grid.s[self.hover_idx]:.4f}"
            p_text = f"{self.grid.p[self.hover_idx]:.4f}"
        else:
            idx_text = vel_text = "(-, -)"
            type_text = div_text = s_text = p_text = "-"
            
        self.cell_type.title = f"Cell Type: {type_text}"
        self.cell_idx.title = f"Cell Index: {idx_text}"
        self.cell_vel.title = f"Velocity: {vel_text}"
        self.cell_div.title = f"Divergence: {div_text}"
        self.cell_s.title = f"Smoke Density: {s_text}"
        self.cell_p.title = f"Pressure: {p_text}"
        
        
    def update(self, dt) -> None:
        
        for widget in chain(self.infos, self.btns, self.dropdowns, self.slidebars):
            widget.update(self.hovering.id, -1)
    
    def update_grid(self, screen:pg.Surface) -> None:
            
        if self.wind_tunnel:
            self.grid.u[1:2, 1:-1] = 500 / self.dt / self.grid.cell_px / self.grid.scale
            self.grid.s[1, self.grid.num_cells//2-2:self.grid.num_cells//2+1] = 1
            
        self.grid.set_boundary_values()
        self.grid.calculate_divergence()
        self.grid.calculate_pressure(100, 1.5)
        self._update_text()
        self.draw_grid(screen)
        
        self.grid.project_velocities()
        self.grid.set_boundary_values()
        self.grid.advect_velocities()
        
        self.grid.calculate_divergence()
        self.grid.calculate_pressure(100, 1)
        self.grid.project_velocities()
        self.grid.advect_smoke()
        
    
    #   ==========[ DRAW ]==========
    def draw_grid(self, screen:pg.Surface) -> None:
        
        match self.dsp_field:
            case "Smoke": img = self.grid.get_smoke_field_img()
            case "Divergence": img = self.grid.get_divergence_field_img()
            case "Pressure": img = self.grid.get_pressure_field_img()
        screen.blit(img, self.grid.rect)
        if self.shw_vel_btn.text == "On": screen.blit(self.grid.get_velocity_field_img(), self.grid.rect)
        screen.blit(self.grid.get_walls_field_img(), self.grid.rect)
        
        
    def draw(self, screen:pg.Surface) -> None:
        
        screen.blit(self.title_surf, TITLE_POS)     #   draw title
        self.update_grid(screen)
        
        for widget in chain(self.infos, self.btns, self.dropdowns, self.slidebars):
            if isinstance(widget, Dropdown):
                widget.draw_parent(screen)
                continue
            widget.draw(screen)
            
        for dropdown in self.dropdowns:
            if dropdown.show:
                dropdown.draw_children(screen)
                break                
            
        for info in self.infos:
            if self.hovering.id == info.id:
                info.draw_description(screen)
                break