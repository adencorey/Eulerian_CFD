import numpy as np
import pygame as pg

from cfd.interface.config import config
from cfd.settings.manager import settings
from cfd.simulation.algorithms import *


class Grid:
    
    def __init__(self, dt:float) -> None:
        
        self.dt = dt
        self.num_cells = 256
        self.scale = (self.num_cells - 2) / 32
        self.env_length = 10                    #   10 meters
        self.cell_size = self.env_length / (self.num_cells - 2)
        
        self.cell_px = int(0.9 * config.height / self.num_cells)
        self.grid_size = (self.num_cells * self.cell_px * np.ones(2)).astype(np.uint16)
        self.surf = pg.Surface(self.grid_size)
        self.rect = self.surf.get_rect(bottomright=np.array((config.width, config.height)) - int((0.98 * config.height - self.grid_size[1]) / 2) * np.ones(2))
        
        # create grid of positions (cell centers)
        side = np.arange(self.num_cells) * self.cell_px + self.cell_px // 2
        x, y = np.meshgrid(side, side)
        self.pos = np.stack((x, y))
        
        self.density = 1
        COLLOCATED_GRID = (self.num_cells, self.num_cells)
        
        #   wall cells  (1 - valid cell; 0 - wall cell)
        self.w = np.ones(COLLOCATED_GRID, dtype=np.uint8)
        self.w[1:-1, 1] = 0
        self.w[1:-1, -2] = 0
        self.w[1, 2:-2] = 0
        self.w[-2, 2:-2] = 0
        
        #   velocity field
        self.u = np.zeros((self.num_cells + 1, self.num_cells), dtype=np.float64)
        self.v = np.zeros((self.num_cells, self.num_cells + 1), dtype=np.float64)
        self.nu = np.zeros((self.num_cells + 1, self.num_cells), dtype=np.float64)
        self.nv = np.zeros((self.num_cells, self.num_cells + 1), dtype=np.float64)
        
        #   divergence field
        self.div = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        
        #  smoke field
        self.s = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        self.ns = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        
        #   pressure field
        self.p = np.zeros(COLLOCATED_GRID, dtype=np.float64)
    
    
    #   ==========[ UTILITIES ]==========        
    def hovered_cell(self, mouse_pos) -> tuple | None:
        idx = None
        if self.rect.collidepoint(mouse_pos):
            idx = (np.array(mouse_pos) - np.array(self.rect.topleft)) // self.cell_px
            idx = None if np.any((idx < 0) | (idx >= self.num_cells)) else tuple(idx.tolist())
        return idx
    
    def shrink_field(self, arr: np.ndarray) -> np.ndarray:
        side = arr.shape[0]
        return arr if side <= 66 or side % 2 == 1 else self.shrink_field(0.25 * arr.reshape(side // 2, 2, side // 2, 2).sum(axis=1).sum(axis=2))
    
    #   ==========[ UPDATE ]==========
    def set_boundary_values(self) -> None:
        free_slip_wall_check(self.num_cells, self.w, self.u, self.v, self.s)
    
    def calculate_divergence(self) -> None:
        get_divergence_field(self.num_cells, self.cell_size, self.w, self.u, self.v, self.div)
    
    def calculate_pressure(self, iter, sor_weight) -> None:
        self.p = poisson_pressure_solve(self.dt, self.num_cells, self.cell_size ** 2, self.density, self.w, self.div, iter, sor_weight)
        
    def project_velocities(self) -> None:
        pressure_projection(self.dt, self.num_cells, self.cell_size, self.density, self.w, self.p, self.u, self.v)
    
    def advect_velocities(self) -> None:
        semi_lagrangian_advect_velocity(self.dt, self.cell_size, self.num_cells, self.w, self.u, self.v, self.nu, self.nv)
        self.u[:, :] = self.nu
        self.v[:, :] = self.nv
    
    def advect_smoke(self) -> None:
        semi_lagrangian_advect_smoke(self.dt, self.cell_size, self.num_cells, self.w, self.s, self.ns, self.u, self.v)
        self.s[:, :] = self.ns
        
    def diffuse_smoke(self, iter, sor_weight) -> None:
        smoke_diffusion(self.dt, self.num_cells, self.w, self.s, iter, sor_weight)
    
    def diffuse_velocities(self, iter, sor_weight) -> None:
        velocity_diffusion(self.dt, self.num_cells, self.w, self.u, self.v, iter, sor_weight)
        
    #   ==========[ DRAW ]==========
    def get_walls_field_img(self, img:np.ndarray) -> None:

        is_wall = self.w == 0
        img[is_wall] = config.hvr_clr
    
    def get_smoke_field_img(self, img:np.ndarray) -> None:
        
        s = self.s.copy()
        if settings.theme_name == "light":
            s = 1 - s
        c = (255 * s).astype(np.uint8)
        img[:, :] = np.stack([c] * 3, axis=-1)
    
    def get_divergence_field_img(self, img:np.ndarray) -> None:
        
        div = np.clip(self.div, -5, 5)
        norm = div / 5
        r = (255 * np.where(norm > 0, norm, 0)).astype(np.uint8)        #   red if outflow
        g = np.zeros_like(norm)
        b = (255 * np.where(norm < 0, -norm, 0)).astype(np.uint8)       #   blue if inflow
        img[:, :] = np.stack((r, g, b), axis=-1)
    
    def get_pressure_field_img(self, img) -> None:
        
        #   normalise
        p = self.p
        max_p = np.percentile(np.abs(p), 95)   #   get 98th percentile to remove velocity spikes
        np.clip(p, -max_p, max_p, out=p)
        if max_p <= 0.1 * self.density:
            norm = 0.5 * np.ones_like(p)
        else:
            norm = 0.5 * (p / max_p) + 0.5
        
        #   jet colourmap (rainbow gradient)
        r = np.where(norm < 0.5, 0, np.where(norm < 0.75, (255 * 4 * (norm - 0.5)), 255)).astype(np.uint8)
        g = np.where(norm < 0.25, (255 * 4 * norm), np.where(norm < 0.75, 255, (255 * 4 * (1 - norm)))).astype(np.uint8)
        b = np.where(norm < 0.25, 255, np.where(norm < 0.5, (255 * 4 * (0.5 - norm)), 0)).astype(np.uint8)
        scale = np.clip(1.5 * self.s, 0, 1)
        img[:, :] = np.stack((r, g, b), axis=-1)
    """
    def get_pressure_field_img(self, img) -> None:
        #   normalisation
        p = self.p
        abs_max = np.max(np.abs(p))
        norm = p / abs_max if abs_max > 0 else np.zeros_like(p)
        norm = 0.5 * norm + 0.5
        
        #   jet colourmap (rainbow gradient)
        r = np.where(norm < 0.5, 0, np.where(norm < 0.75, (255 * 4 * (norm - 0.5)), 255)).astype(np.uint8)
        g = np.where(norm < 0.25, (255 * 4 * norm), np.where(norm < 0.75, 255, (255 * 4 * (1 - norm)))).astype(np.uint8)
        b = np.where(norm < 0.25, 255, np.where(norm < 0.5, (255 * 4 * (0.5 - norm)), 0)).astype(np.uint8)
        img[:, :] = np.stack((r, g, b), axis=-1)
    """
        
    def get_velocity_field_img(self, img:np.ndarray) -> None:
        
        u = 0.5 * (self.u[:-1, :] + self.u[1:, :])
        v = 0.5 * (self.v[:, :-1] + self.v[:, 1:])

        nu, nv = self.shrink_field(u), self.shrink_field(v)
        factor = u.shape[0] / nu.shape[0]
        
        vel = np.stack((-nv, nu))  #  negate v for screen coordinates
        
        mag = np.zeros_like(nu)
        mag[1:-1, 1:-1] = np.sqrt(np.sum(vel[:, 1:-1, 1:-1] ** 2, axis=0)) / self.cell_size * self.cell_px
        mag_clipped = np.clip(mag, 0, self.env_length / self.cell_size * 2 * self.cell_px * factor)
        
        is_mag = mag > 0
        d = np.zeros_like(vel)
        d[:, is_mag] = vel[:, is_mag] / mag[is_mag]     #   get direction vector where mag > 0
        
        #   draw velocity lines
        steps = np.linspace(0, 1, 25)
        position = np.array((self.shrink_field(self.pos[0]), self.shrink_field(self.pos[1])))
        for step in steps:
            pos = (position[:, is_mag] + mag_clipped[is_mag] * d[:, is_mag] * step).astype(int)
            valid = (pos[0] > 0) & (pos[0] < self.grid_size[0]) & (pos[1] > 0) & (pos[1] < self.grid_size[1])
            colour = (128, 128, 128) if step < 0.6 else (0, 128, 128)
            img[pos[1][valid], pos[0][valid]] = colour