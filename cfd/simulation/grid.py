import numpy as np
import pygame as pg

from cfd.interface.config import config
from cfd.settings.manager import settings
from cfd.simulation.algorithms import *


class Grid:
    
    def __init__(self, dt:float) -> None:
        
        self.dt = dt
        self.num_cells = 64 + 2
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
        
        COLLOCATED_GRID = (self.num_cells, self.num_cells)
        
        #   wall cells  (1 - valid cell; 0 - wall cell)
        self.w = np.ones(COLLOCATED_GRID, dtype=np.uint8)
        self.w[1:-1, 1] = 0
        self.w[1:-1, -2] = 0
        #self.w[1, 2:-2] = 0
        #self.w[-2, 2:-2] = 0
        
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
    
    #   ==========[ UPDATE ]==========
    def set_boundary_values(self) -> None:
        free_slip_boundary_check(self.num_cells, self.w, self.u, self.v, self.s)
        ghost_cells_boundary_check(self.u, self.v, self.s)
        
    def calculate_divergence(self) -> None:
        get_divergence_field(self.num_cells, self.cell_size, self.w, self.u, self.v, self.div)
    
    def calculate_pressure(self, iter, sor_weight) -> None:
        self.p = poisson_pressure_solve(self.dt, self.num_cells, self.cell_size ** 2, self.w, self.div, iter, sor_weight)
        
    def project_velocities(self) -> None:
        pressure_projection(self.dt, self.num_cells, self.cell_size, self.w, self.p, self.u, self.v)
    
    def advect_velocities(self) -> None:
        semi_lagrangian_advect_velocity(self.dt, self.cell_size, self.num_cells, self.w, self.u, self.v, self.nu, self.nv)
        self.u[:, :] = self.nu[:, :]
        self.v[:, :] = self.nv[:, :]
    
    def advect_smoke(self) -> None:
        semi_lagrangian_advect_smoke(self.dt, self.cell_size, self.num_cells, self.w, self.s, self.ns, self.u, self.v)
        self.s[:, :] = self.ns[:, :]
        
    #   ==========[ DRAW ]==========
    def get_walls_field_img(self, img:np.ndarray) -> None:

        is_wall = self.w == 0
        img[is_wall] = config.bg_clr
    
    def get_smoke_field_img(self, img:np.ndarray) -> pg.Surface:
        
        s = self.s.copy()
        if settings.theme_name == "light":
            s = 1 - s
        c = (255 * s).astype(np.uint8)
        img[:, :] = np.stack([c] * 3, axis=-1)
    
    def get_divergence_field_img(self, img:np.ndarray) -> pg.Surface:
        
        div = np.clip(self.div, -5, 5)
        norm = div / 5
        r = (255 * np.where(norm > 0, norm, 0)).astype(np.uint8)
        g = np.zeros_like(norm)
        b = (255 * np.where(norm < 0, -norm, 0)).astype(np.uint8)   
        img[:, :] = np.stack((r, g, b), axis=-1)
    
    def get_pressure_field_img(self, img) -> pg.Surface:
        
        p = np.clip(self.p, -3000, 3000)
        norm: np.ndarray = (p + 3000) / 6000
        r = np.where(norm < 0.5, 0, np.where(norm < 0.75, (255 * 4 * (norm - 0.5)), 255)).astype(np.uint8)
        g = np.where(norm < 0.25, (255 * 4 * norm), np.where(norm < 0.75, 255, (255 * 4 * (1 - norm)))).astype(np.uint8)
        b = np.where(norm < 0.25, 255, np.where(norm < 0.5, (255 * 4 * (0.5 - norm)), 0)).astype(np.uint8)
        img[:, :] = np.stack((r, g, b), axis=-1)
        
    def get_velocity_field_img(self, img:np.ndarray) -> pg.Surface:

        #   calculate velocity vectors at cell centers
        u = 0.5 * (self.u[:-1, :] + self.u[1:, :])
        v = 0.5 * (self.v[:, :-1] + self.v[:, 1:])
        vec = np.stack((-v, u))  #  negate v for screen coordinates
        
        #   calculate magnitude
        mag: np.ndarray = np.sqrt(np.sum(vec ** 2, axis=0)) * self.scale
        mag_clipped = np.clip(mag, 0, 2 * self.cell_px * self.scale)

        #   direction vector
        dir = np.zeros_like(vec)
        mask = mag > 0
        dir[:, mask] = vec[:, mask] / mag[mask]     #   only calculates for magnitudes > 0
        
        #   draw velocity lines
        steps = np.linspace(0, 1, 50)
        for step in steps:
            pos = (self.pos + 0.4 * dir * mag_clipped * step).astype(int)
            
            valid_x = (pos[0] >= 0) & (pos[0] < self.grid_size[0])
            valid_y = (pos[1] >= 0) & (pos[1] < self.grid_size[1])
            valid = valid_x & valid_y
            
            colour = (150, 150, 150) if step < 0.7 else (255, 255, 255)
            img[pos[1][valid], pos[0][valid]] = colour