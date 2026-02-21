import pygame as pg
import numpy as np

import logging
from itertools import chain

from cfd.settings.manager import settings
from cfd.interface.config import config
from cfd.interface.widgets import Widget, NULLWIDGET, Info, Dropdown, Slidebar, CheckBox, RectButton
from cfd.helpers.screen import TITLE_POS, get_grid
from cfd.simulation.grid import Grid

logger = logging.getLogger(__name__)

class SimulationScreen:
    
    def __init__(self, app) -> None:
        from cfd.app import App
        self.app: App = app
        
        self.title_surf = config.font["title"].render("Simulation", True, config.main_clr)
        self.control_surf = config.font["sub"].render("Add velocity - LMB drag    Add smoke - RMB drag", True, config.hvr_clr)
        self.wall_surf = config.font["sub"].render("Add Wall - Shift + LMB drag", True, config.hvr_clr)
        self.angle_surf = config.font["sub"].render("Rotate - Mousewheel (Z / X)", True, config.hvr_clr)
        self.grid = Grid(app.project)
                
        drp_dim = (int(0.1 * config.width), int(0.04 * config.height))
        sb_dim = int(0.15 * config.width), int(0.008 * config.height)
        btn_dim = (int(0.1 * config.width), int(0.04 * config.height))
        
        self.dsp_field = "Smoke"
        self.dsp_field_info = Info(name="dsp-field-info", title="Display Field", pos=get_grid(2, 7), description="Select type of field to display.")
        self.dsp_field_drp = Dropdown(name="dsp-field-drp", rect=pg.Rect(get_grid(8, 7), drp_dim), options=["Smoke", "Divergence", "Pressure"], setting=self.dsp_field, anchor="w", font=config.font["par"])
        self.shw_vel_chk = CheckBox(name="shw-vel-chk", pos=get_grid(2, 8.5), text="Show velocity arrows")
        self.smoke_only_chk = CheckBox(name="smoke-only-chk", pos=get_grid(8, 8.5), text="Smoke only")
        
        self.brush_info = Info(name="brush_size_info", title="Brush Size", pos=get_grid(2, 10))
        self.brush_sb = Slidebar(name="brush_size_sb", rect=pg.Rect(get_grid(9, 10), sb_dim), min_val=1, max_val=int(0.25 * self.grid.num_cells), step=1, default=int(0.1 * self.grid.num_cells))
        
        self.shw_debug_chk = CheckBox(name="shw-debug-chk", pos=get_grid(2, 11.5), text="Show debug screen")
        
        self.config_env = RectButton(name="config-env-btn", rect=pg.Rect(get_grid(2, 24), (int(0.18 * config.width), int(0.05 * config.height))), text="Configure Environment")
        
        #   ==========[ DEBUG SCREEN ]==========
        self.total_div = Info(name="total_div_info", title="Total Divergence: 0", pos=get_grid(2, 14), description="Sum of magnitude of divergence of all cells, simulation will be less accurate if this number is huge. Divergence of a cell is how much velocity field diverge or converge around it", font=config.font["sub"], desc_font=config.font["sml"])
        self.total_s = Info(name="total_s_info", title="Total Smoke Density: 0", pos=get_grid(2, 14.75), description="Sum of smoke density of all cells.", font=config.font["sub"], desc_font=config.font["sml"])
        
        self.cell_type = Info(name="cell_type_info", title="Cell Type: -", pos=get_grid(2, 16), description="Cell type of hovering cell, fluid cell - 1; wall cell - 0.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_idx = Info(name="cell_idx_info", title="Cell Index: (-, -)", pos=get_grid(2, 16.75), description="Grid index of hovering cell in (row, column), starts with top-left corner with index (0, 0).", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_vel = Info(name="cell_vel_info", title="Velocity: (-, -)", pos=get_grid(2, 17.5), description="Velocity vector of hovering cell in meter per second.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_div = Info(name="cell_div_info", title="Divergence: -", pos=get_grid(2, 18.25), description="Divergence of hovering cell, diverging - positive; converging - negative.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_s = Info(name="cell_s_info", title="Smoke Density: -", pos=get_grid(2, 19), description="Smoke density of hovering cell from 0 to 1.", font=config.font["sub"], desc_font=config.font["sml"])
        self.cell_p = Info(name="cell_p_into", title="Pressure: -", pos=get_grid(2, 19.75), description="Relative pressure of hovering cell, high - positive; normal - zero; low - negative.", font=config.font["sub"], desc_font=config.font["sml"])
        
        self.proj_field_chk = CheckBox(name="proj-field-chk", pos=get_grid(2, 20.5), text="Enable projection step (clears out divergence)", font=config.font["sub"], checked=True)
        self.adv_field_chk = CheckBox(name="adv-field-chk", pos=get_grid(2, 21.25), text="Enable advection step (transport velocities and smoke)", font=config.font["sub"], checked=True)
        
        #   ==========[ CONFIGURE ENVIRONMENT SCREEN ]==========
        self.clr_init_btn = RectButton(name="clr-init-btn", rect=pg.Rect(get_grid(2, 7), (int(0.15 * config.width), int(0.05 * config.height))), text="Clear Configurations")
        self.wind_btn = RectButton(name="wind-btn", rect=pg.Rect(get_grid(7, 7), (int(0.15 * config.width), int(0.05 * config.height))), text="Wind Tunnel")
        
        self.vel_mag_info = Info(name="vel-mag-info", title="Velocity Magnitude", pos=get_grid(2, 15), description="Speed of fluid in that cell, measured in ms^-1.")
        self.vel_mag_sb = Slidebar(name="vel-mag-sb", rect=pg.Rect(get_grid(7, 17), sb_dim), min_val=1, max_val=50, step=1, default=5)
        
        self.angle = 0
        self.angle_info = Info(name="angle-info", title="Velocity Direction: 0 deg", pos=get_grid(2, 20), description="Angle of velocity in degrees, measured from positive horizontal (right) and increases anti-clockwise.")
        
        self.save_btn = RectButton(name="save-env-btn", rect=pg.Rect(get_grid(2, 24), btn_dim), text="Save")
        self.cancel_btn = RectButton(name="cancel-env-btn", rect=pg.Rect(get_grid(7, 24), btn_dim), text="Cancel")
        
        
        self.infos: list[Info] = [self.dsp_field_info, self.brush_info]
        self.drps: list[Dropdown] = [self.dsp_field_drp]
        self.sbs: list[Slidebar] = [self.brush_sb]
        self.chks: list[CheckBox] = [self.shw_debug_chk, self.shw_vel_chk, self.smoke_only_chk]
        self.btns: list[RectButton] = [self.config_env]
        
        self.debug_infos: list[Info] = [self.total_div, self.total_s, self.cell_type, self.cell_idx, self.cell_vel, self.cell_div, self.cell_s, self.cell_p]
        self.debug_chks: list[CheckBox] = [self.proj_field_chk, self.adv_field_chk]
        
        self.config_infos: list[Info] = [self.brush_info, self.angle_info, self.vel_mag_info]
        self.config_sbs: list[Slidebar] = [self.brush_sb, self.vel_mag_sb]
        self.config_btns: list[RectButton] = [self.save_btn, self.cancel_btn, self.clr_init_btn, self.wind_btn]
        
        self.hover_idx: tuple[int, int] = None
        self.configuring = False
        
        self.base_img = np.zeros([self.grid.num_cells, self.grid.num_cells, 3], dtype=np.uint8)
        self.vel_img = np.zeros((self.grid.dim[1], self.grid.dim[0], 3), dtype=np.uint8)
        self.img_surf = pg.surfarray.make_surface(self.vel_img)
        
    def _widgets(self) -> chain[Widget]:
        widgets = chain(self.drps, self.infos, self.sbs, self.chks, self.btns)
        if self.configuring: return chain(self.config_infos, self.config_sbs, self.config_btns)
        if self.shw_debug_chk.checked: return chain(widgets, self.debug_infos, self.debug_chks)
        return widgets
    
    def reset_config(self) -> None:
        
        self.grid.u0[:, :] = 0
        self.grid.v0[:, :] = 0
        self.grid.s0[:, :] = 0
        self.grid.w[:, :] = 1
        
    #   ==========[ EVENT HANDLING ]==========
    def _handle_hover(self, mouse_pos: tuple) -> None:        
        
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
            
        elif self.app.hovering.id == self.config_env.id:
            self.shw_debug_chk.checked = False
            self.configuring = True
            self.dsp_field = "Config"
            self.grid.reset()
        
        elif self.app.hovering.id == self.cancel_btn.id:
            self.__init__(self.app)
        
        elif self.app.hovering.id == self.save_btn.id:
            self.grid.save_conditions(self.app.project)            
            self.__init__(self.app)
        
        elif self.app.hovering.id == self.clr_init_btn.id:
            self.reset_config()
        
        elif self.app.hovering.id == self.wind_btn.id:
            self.reset_config()
            mid = self.grid.num_cells // 2
            length = self.grid.num_cells // 20
            self.grid.w[1, :] = self.grid.w[-2, :] = 0
            self.grid.u0[:, 1:4] = self.grid.env_length * 2
            self.grid.s0[mid-length:mid+length, 1:4] = 1
            
        else:
            for widget in self._widgets():
                if self.app.hovering.id == widget.id:
                    if isinstance(widget, Slidebar):
                        widget.dragging = True
                    elif isinstance(widget, CheckBox):
                        widget.checked = not widget.checked
                    break
        
        logger.debug(f"Clicked {self.app.hovering.name}")
        if event: pg.event.post(pg.event.Event(event, extra_data))
    
    def _handle_drag(self, mouse_pos, left) -> None:
        
        if left:
            for slidebar in chain(self.sbs, self.config_sbs):
                if slidebar.dragging:
                    slidebar.x_pos = mouse_pos[0]
                    break
    
    def _handle_mouse(self, mouse_rel, left, mid, right, shift) -> None:
        
        if not any([left, mid, right, shift]): return
        
        i, j = self.hover_idx
        radius = int(self.brush_sb.value)
        
        i_start = max(i - radius, 1)
        j_start = max(j - radius, 1)
        i_end = min(i + radius + 1, self.grid.num_cells - 1)
        j_end = min(j + radius + 1, self.grid.num_cells - 1)
        
        #   create weight matrix to create smooth decrease from center
        x_span = np.arange(i_start, i_end)
        y_span = np.arange(j_start, j_end)
        x, y = np.meshgrid(x_span, y_span, indexing='ij')
        
        weight = 1 - (np.hypot(x - i, y - j) / radius)
        np.clip(weight, 0, 1, out=weight)
        brush_area = slice(i_start, i_end), slice(j_start, j_end)
        
        if not self.configuring:
            if left:
                rx, ry = mouse_rel
                k = self.grid.cell_size / self.grid.cell_px / self.grid.dt * weight
                self.grid.u[brush_area] += k * rx
                self.grid.v[brush_area] -= k * ry
            
            if right:
                self.grid.s[brush_area] += weight
                np.clip(self.grid.s, 0, 1, out=self.grid.s)
        
        else:
            if mid or (shift and left):
                self.grid.w[brush_area] *= 1 - np.clip((weight * radius * 2), 0, 1).astype(np.uint8)
                np.clip(self.grid.w, 0, 1, out=self.grid.w)
            
            elif shift and right:
                self.grid.u0[brush_area] = self.grid.v0[brush_area] = self.grid.s0[brush_area] = 0
                self.grid.w[brush_area] += np.clip((weight * radius * 2), 0, 1).astype(np.uint8)
                np.clip(self.grid.w, 0, 1, out=self.grid.w)
            
            else:
                if left:
                    rad = np.deg2rad(self.angle)
                    self.grid.u0[brush_area] = self.vel_mag_sb.value * np.cos(rad) * np.ones_like(weight)
                    self.grid.v0[brush_area] = self.vel_mag_sb.value * np.sin(rad) * np.ones_like(weight)
                
                if right:
                    self.grid.s0[brush_area] += np.clip((weight * radius * 2), 0, 1).astype(np.uint8)
                    np.clip(self.grid.s0, 0, 1, out=self.grid.s0)
            
        
    def handle_events(self, event: pg.event.Event) -> None:
        
        keys = pg.key.get_pressed()
        mouse = pg.mouse
        mouse_pos = mouse.get_pos()
        mouse_rel = mouse.get_rel()
        left, mid, right = mouse.get_pressed()
        if event.type == pg.MOUSEMOTION:
            self._handle_hover(mouse_pos)
            self.hover_idx = self.grid.hovered_cell(mouse_pos)
            self._handle_drag(mouse_pos, left)
        if self.hover_idx is not None:
            self._handle_mouse(mouse_rel, left, mid, right, keys[pg.K_LSHIFT])
        if event.type == pg.MOUSEBUTTONDOWN and left:
            self._handle_click()
        if event.type == pg.MOUSEBUTTONUP and not left:
            for sb in chain(self.sbs, self.config_sbs):
                if sb.dragging: sb.dragging = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_z: self.angle = (self.angle + 1) % 360
            if event.key == pg.K_x: self.angle = (self.angle - 1) % 360
            
        if event.type == pg.MOUSEWHEEL:
            self.angle = (self.angle + 5 * event.y) % 360
        
    
    
    #   ==========[ UPDATE ]==========
    def _update_text(self) -> None:
        
        if self.shw_debug_chk.checked:
            self.total_div.title = f"Total Divergence: {np.sum(np.abs(self.grid.div)):.4f}"
            self.total_s.title = f"Total Smoke Density: {np.sum(self.grid.s):.4f}"
            
            if self.hover_idx is not None:
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
            
        if self.configuring:
            self.angle_info.title = f"Velocity Direction: {self.angle} deg"
        
        
    def update(self) -> None:

        for widget in self._widgets():
            widget.update(self.app.hovering.id, -1)
        self._update_grid()
        
    def _update_screen(self) -> None:
        
        self._update_text()
        match self.dsp_field:
            case "Smoke": self.grid.get_smoke_field_img(self.base_img)
            case "Divergence": self.grid.get_divergence_field_img(self.base_img)
            case "Pressure": self.grid.get_pressure_field_img(self.base_img, smoke_only=self.smoke_only_chk.checked)
            case "Config": self.grid.get_smoke_field_img(self.base_img, initial=True)
        self.vel_img[:, :, :] = 0
        
        if self.configuring:
            self.grid.get_velocity_field_img(self.vel_img, initial=True)
        elif self.shw_vel_chk.checked:
            self.grid.get_velocity_field_img(self.vel_img)


    def _update_grid(self) -> None:
        
        if not self.configuring:
            project = self.proj_field_chk.checked
            advect = self.adv_field_chk.checked
            iter = settings.iterator
            sor = settings.sor_weight
                    
            #   1. add external sources
            self.grid.add_external_forces()            
            self.grid.set_boundary_values()
            
            #   2. move smoke and velocity around
            if advect:
                self.grid.advect_smoke()
                self.grid.advect_velocities()
                np.clip(self.grid.s, 0, 1, out=self.grid.s)
            
            #   3. clears out divergence to enforce incompressibility
            self.grid.calculate_divergence()
            self.grid.calculate_pressure(iter, sor)
            if project: self.grid.project_velocities()

            self.grid.set_boundary_values()
        
        #   4. update screen  
        self.grid.calculate_divergence()
        self._update_screen()

    
    #   ==========[ DRAW ]==========
    def draw_grid(self, screen:pg.Surface) -> None:
        
        self.grid.get_walls_field_img(self.base_img)
        base_surf = pg.surfarray.make_surface(self.base_img)
        self.img_surf.blit(pg.transform.scale(base_surf, self.grid.dim), (0, 0))
        screen.blit(self.img_surf, self.grid.rect)

        if self.shw_vel_chk.checked or self.configuring:
            vel_surf = pg.surfarray.make_surface(self.vel_img)
            vel_surf.set_colorkey((0, 0, 0))
            screen.blit(vel_surf, self.grid.rect)
        
        
    def draw(self, screen:pg.Surface) -> None:
        
        screen.blit(self.title_surf, TITLE_POS)                             #   title
        screen.blit(self.control_surf, get_grid(2, 26))                     #   controls
        if self.configuring:
            screen.blit(self.wall_surf, get_grid(2, 27))                    #   wall
            screen.blit(self.angle_surf, get_grid(2, 21))                   #   angle
        self.draw_grid(screen)

        for widget in self._widgets():
            if widget.id == self.smoke_only_chk.id:
                if self.dsp_field != "Pressure": continue
                
            if isinstance(widget, Dropdown):
                widget.draw_parent(screen)
                continue
            widget.draw(screen)
            
        for dropdown in self.drps:
            if dropdown.show:
                dropdown.draw_children(screen)
                break                
            
        for info in chain(self.infos, self.debug_infos, self.config_infos):
            if self.app.hovering.id == info.id:
                info.draw_description(screen)
                break
            
        #   draw angle indicator
        if self.configuring and self.hover_idx is not None:
            rad = np.deg2rad(self.angle)
            length = 0.1 * self.grid.env_length / self.grid.cell_size * self.grid.cell_px
            start = pg.mouse.get_pos()
            end = np.array(start) + length * np.array([np.cos(rad), -np.sin(rad)])
            pg.draw.line(screen, (0, 150, 255), start, end, int(length / 20))