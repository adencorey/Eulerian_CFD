import pygame as pg
import numpy as np

import logging
from itertools import chain

from cfd.settings.manager import settings
from cfd.interface.config import config, Events, Screens
from cfd.interface.widgets import Widget, NULLWIDGET, Info, Dropdown, Slidebar, CheckBox, RectButton
from cfd.helpers.screen import TITLE_POS, get_grid
from cfd.simulation.grid import Grid

logger = logging.getLogger(__name__)

class SimulationScreen:
    
    def __init__(self, app) -> None:
        from cfd.app import App
        self.app: App = app
        
        self.title_surf = config.font["title"].render("Simulation", True, config.main_clr)
        self.grid = Grid(app.project)
                
        self.drp_dim = (int(0.1 * config.width), int(0.04 * config.height))
        self.sb_dim = int(0.15 * config.width), int(0.008 * config.height)
        self.btn_dim = (int(0.1 * config.width), int(0.04 * config.height))
        
        self.dsp_field = "Smoke"
        self.dsp_field_info = Info(name="dsp-field-info", title="Display Field", pos=get_grid(2, 6), description="Select type of field to display.")
        self.dsp_field_drp = Dropdown(name="dsp-field-drp", rect=pg.Rect(get_grid(8, 6), self.drp_dim), options=["Smoke", "Divergence", "Pressure"], setting=self.dsp_field, anchor="w", font=config.font["par"])
        self.shw_vel_chk = CheckBox(name="shw-vel-chk", pos=get_grid(2, 7.5), text="Show velocity arrows")
        
        
        self.brush_size_info = Info(name="brush_size_info", title="Brush Size", pos=get_grid(2, 9), description="Paint brush size.")
        self.brush_size_sb = Slidebar(name="brush_size_sb", rect=pg.Rect(get_grid(9, 9), self.sb_dim), min_val=1, max_val=int(0.25 * self.grid.num_cells), step=1, default=int(0.1 * self.grid.num_cells))
        
        self.shw_debug_chk = CheckBox(name="shw-debug-chk", pos=get_grid(2, 10.5), text="Show debug screen")
        
        self.edit_env = RectButton(name="edit-env-btn", rect=pg.Rect(get_grid(2, 25), (int(0.18 * config.width), int(0.05 * config.height))), text="Configure Environment")
        
        #   ==========[ DEBUG SCREEN ]==========
        self.total_div = Info(name="total_div_info", title="Total Divergence: 0", pos=get_grid(2, 12), description="Sum of magnitude of divergence of all cells, simulation will be less accurate if this number is huge. Divergence of a cell is how much velocity field diverge or converge around it", font=config.font["sub"], desc_font=config.font["sml"])
        self.total_s = Info(name="total_s_info", title="Total Smoke Density: 0", pos=get_grid(2, 12.75), description="Sum of smoke density of all cells.", font=config.font["sub"], desc_font=config.font["sml"])
        
        self.cell_type = Info(name="cell_type_info", title="Cell Type: -", pos=get_grid(2, 14), description="Cell type of hovering cell, fluid cell - 1; wall cell - 0.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_idx = Info(name="cell_idx_info", title="Cell Index: (-, -)", pos=get_grid(2, 14.75), description="Grid index of hovering cell in (row, column), starts with top-left corner with index (0, 0).", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_vel = Info(name="cell_vel_info", title="Velocity: (-, -)", pos=get_grid(2, 15.5), description="Velocity vector of hovering cell in meter per second.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_div = Info(name="cell_div_info", title="Divergence: -", pos=get_grid(2, 16.25), description="Divergence of hovering cell, diverging - positive; converging - negative.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_s = Info(name="cell_s_info", title="Smoke Density: -", pos=get_grid(2, 17), description="Smoke density of hovering cell from 0 to 1.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_p = Info(name="cell_p_into", title="Pressure: -", pos=get_grid(2, 17.75), description="Relative pressure of hovering cell, high - positive; normal - zero; low - negative.", font=config.font["sub"], desc_font=config.font["sml"])
        
        self.proj_field_chk = CheckBox(name="proj-field-chk", pos=get_grid(2, 18.5), text="Enable projection step (clears out divergence)", font=config.font["sub"], checked=True)
        self.adv_field_chk = CheckBox(name="adv-field-chk", pos=get_grid(2, 19.25), text="Enable advection step (transport velocities and smoke)", font=config.font["sub"], checked=True)
        
        
        self.infos: list[Info] = [self.dsp_field_info, self.brush_size_info]
        self.drps: list[Dropdown] = [self.dsp_field_drp]
        self.sbs: list[Slidebar] = [self.brush_size_sb]
        self.chks: list[CheckBox] = [self.shw_debug_chk, self.shw_vel_chk]
        self.btns: list[RectButton] = [self.edit_env]
        
        self.debug_infos: list[Info] = [self.total_div, self.total_s, self.cell_type, self.cell_idx, self.cell_vel, self.cell_div, self.cell_s, self.cell_p]
        self.debug_chks: list[CheckBox] = [self.proj_field_chk, self.adv_field_chk]
        
        self.hover_idx: tuple[int, int] = None
        
        self.base_img = np.zeros([self.grid.num_cells, self.grid.num_cells, 3], dtype=np.uint8)
        self.vel_img = np.zeros((self.grid.dim[1], self.grid.dim[0], 3), dtype=np.uint8)
        self.img_surf = pg.surfarray.make_surface(self.vel_img)
        self.wind_tunnel = False
        
    def get_widget_chain(self, debug = False) -> chain[Widget]:
        widgets = chain(self.drps, self.infos, self.sbs, self.chks, self.btns)
        if not debug: return widgets
        return chain(widgets, self.debug_infos, self.debug_chks)
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:        
        
        hovering = self.app.hovering
        hovered = NULLWIDGET
        
        for widget in self.get_widget_chain(self.shw_debug_chk.checked):
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

        elif self.dsp_field_drp.hovering.name:
            self.dsp_field = self.dsp_field_drp.hovering.text
            self.dsp_field_drp.clicked(self.dsp_field)
            
        elif self.app.hovering.id == self.edit_env.id:
            event = Events.SCREEN_SWITCH
            extra_data["screen_id"] = Screens.CONFIG_INIT_PARAM
            
        else:
            for widget in self.get_widget_chain(self.shw_debug_chk.checked):
                if self.app.hovering.id == widget.id:
                    if isinstance(widget, Slidebar):
                        widget.dragging = True
                    elif isinstance(widget, CheckBox):
                        widget.checked = not widget.checked
                    break
        
        logger.debug(f"Clicked {self.app.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
    
    def _handle_drag(self, mouse_pos, mouse_rel, left, mid, right) -> None:
        
        if left:
            for slidebar in self.sbs:
                if slidebar.dragging:
                    slidebar.x_pos = mouse_pos[0]
                    break
                    
        #   external velocity / smoke density by user
        if self.hover_idx:
            i, j = self.hover_idx
            radius = int(self.brush_size_sb.value)
            
            i_start = max(i - radius, 1)
            j_start = max(j - radius, 1)
            i_end = min(i + radius + 1, self.grid.num_cells - 1)
            j_end = min(j + radius + 1, self.grid.num_cells - 1)
            
            #   create weight matrix to create smooth decrease from center
            x_span = np.arange(i_start, i_end)
            y_span = np.arange(j_start, j_end)
            x, y = np.meshgrid(x_span, y_span, indexing='ij')
            weight = 1 - np.hypot(x - i, y - j) / radius
            np.clip(weight, 0, 1, out=weight)
            
            if left:
                rx, ry = mouse_rel
                k = self.grid.cell_size / self.grid.cell_px / self.grid.dt * weight
                self.grid.u[i_start:i_end, j_start:j_end] += k * rx
                self.grid.v[i_start:i_end, j_start:j_end] -= k * ry
            
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
        
        
    def update(self) -> None:
        self.grid.dt = 1 / settings.fps
        for widget in self.get_widget_chain(self.shw_debug_chk.checked):
            widget.update(self.app.hovering.id, -1)
        self._update_grid()
        
    def _update_screen(self) -> None:
        
        if self.shw_debug_chk.checked: self._update_text()
        match self.dsp_field:
            case "Smoke": self.grid.get_smoke_field_img(self.base_img)
            case "Divergence": self.grid.get_divergence_field_img(self.base_img)
            case "Pressure": self.grid.get_pressure_field_img(self.base_img)
        self.vel_img[:, :, :] = 0
        if self.shw_vel_chk.checked:
            self.grid.get_velocity_field_img(self.vel_img)


    def _update_grid(self) -> None:
        
        self._update_screen()
        return
            
        project = self.proj_field_chk.checked
        advect = self.adv_field_chk.checked
        iter = 100
        sor = 1.6
        
        #   1. add external sources
        #self.grid.v[1:-1, 1:-1] += self.dt * -9.81      #   gravity

        if self.wind_tunnel:
            self.grid.u[0:2, 1:-1] = 15
            self.grid.s[0, self.grid.num_cells//2-int(self.grid.scale):self.grid.num_cells//2+int(self.grid.scale)+1] = 1
        
        self.grid.set_boundary_values()
            
        #   2. clears out divergence to enforce incompressibility
        if project:
            self.grid.calculate_divergence()
            self.grid.calculate_pressure(iter, sor)
            self.grid.project_velocities()

        #   4. update screen  
        self.grid.calculate_divergence()
        self._update_screen()
        
        #   5. move velocities and smoke
        np.clip(self.grid.s, 0, 1, out=self.grid.s)
        if advect:
            self.grid.advect_smoke()
            self.grid.advect_velocities()
            
        #   6. manage boundary values again
        self.grid.set_boundary_values()   
        
        #self.grid.diffuse_smoke(iter, sor)
        
    
    #   ==========[ DRAW ]==========
    def draw_grid(self, screen:pg.Surface) -> None:
        
        #self.grid.get_walls_field_img(self.base_img)
        base_surf = pg.surfarray.make_surface(self.base_img)
        self.img_surf.blit(pg.transform.scale(base_surf, self.grid.dim), (0, 0))
        screen.blit(self.img_surf, self.grid.rect)

        if self.shw_vel_chk.checked:
            vel_surf = pg.surfarray.make_surface(self.vel_img)
            vel_surf.set_colorkey((0, 0, 0))
            screen.blit(vel_surf, self.grid.rect)
        
        
    def draw(self, screen:pg.Surface) -> None:
        
        screen.blit(self.title_surf, TITLE_POS)     #   draw title
        self.draw_grid(screen)
        
        for widget in self.get_widget_chain(self.shw_debug_chk.checked):
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
            
        if self.shw_debug_chk.checked:
            for info in self.debug_infos:
                if self.app.hovering.id == info.id:
                    info.draw_description(screen)
                    break