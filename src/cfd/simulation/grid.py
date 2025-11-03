import numpy as np
import pygame as pg

from cfd.interface.config import config
from cfd.settings.manager import settings
from cfd.simulation.algorithms import *


class Grid:
    
    def __init__(self, dt:float) -> None:
        
        self.dt = dt
        self.num_cells = 96 + 2
        self.scale = (self.num_cells - 2) / 32
        self.cell_size = 1 / self.scale
        self.cell_px = int(0.9 * config.height / self.num_cells)
        self.grid_size = self.num_cells * self.cell_px * np.ones(2, dtype=np.uint16)
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
        #self.u = np.random.uniform(-1, 1, (self.num_cells + 1, self.num_cells)).astype(np.float64)
        #self.v = np.random.uniform(-1, 1, (self.num_cells, self.num_cells + 1)).astype(np.float64)
        self.u = np.zeros((self.num_cells + 1, self.num_cells), dtype=np.float64)
        self.v = np.zeros((self.num_cells, self.num_cells + 1), dtype=np.float64)
        
        
        #   divergence field
        self.div = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        
        #  smoke field
        self.s = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        
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
        free_slip_boundary_check(self.num_cells, self.w, self.u, self.v)
        ghost_cells_boundary_check(self.u, self.v)
        
    def calculate_divergence(self) -> None:
        self.div = get_divergence_field(self.num_cells, self.cell_size, self.w, self.u, self.v)
    
    def calculate_pressure(self, iter, sor_weight) -> None:
        self.p = poisson_pressure_solve(self.dt, self.num_cells, self.cell_size, self.w, self.div, iter, sor_weight)
        
    def project_velocities(self) -> None:
        pressure_projection(self.dt, self.num_cells, self.cell_size, self.w, self.p, self.u, self.v)
    
    def advect_velocities(self) -> None:
        self.u, self.v = semi_lagrangian_advect_velocity(self.dt, self.cell_px, self.num_cells, self.w, self.u, self.v)
    
    def advect_smoke(self) -> None:
        self.s = semi_lagrangian_advect_smoke(self.dt, self.cell_px, self.num_cells, self.w, self.s, self.u, self.v)
        
    #   ==========[ DRAW ]==========
    def get_walls_field_img(self) -> pg.Surface:
        
        w = self.w
        r = np.where(w == 0, config.bg_clr[0], 0).astype(np.uint8)
        g = np.where(w == 0, config.bg_clr[1], 0).astype(np.uint8)
        b = np.where(w == 0, config.bg_clr[2], 0).astype(np.uint8)
        img = np.stack((r, g, b), axis=-1)
        surface = pg.surfarray.make_surface(img)
        surface.set_colorkey((0, 0, 0))
        return pg.transform.scale(surface, self.grid_size)
    
    def get_smoke_field_img(self) -> pg.Surface:
        
        #   get rgb of every cell according to smoke density
        s = self.s
        if settings.theme_name == "light":
            s = 1 - s
        c = (255 * s).astype(np.uint8)
        img = np.stack((c, c, c), axis=-1)
        surface = pg.surfarray.make_surface(img)
        return pg.transform.scale(surface, self.grid_size)
    
    def get_divergence_field_img(self) -> pg.Surface:
        
        div = np.clip(self.div, -25, 25)
        norm = div / 25
        r = (255 * np.where(norm > 0, norm, 0)).astype(np.uint8)
        g = np.zeros_like(norm)
        b = (255 * np.where(norm < 0, -norm, 0)).astype(np.uint8)   
        img = np.stack((r, g, b), axis=-1)
        surface = pg.surfarray.make_surface(img)
        return pg.transform.scale(surface, self.grid_size)
    
    def get_pressure_field_img(self) -> pg.Surface:
        
        p = np.clip(self.p, -3000, 3000)
        norm: np.ndarray = (p + 3000) / 6000
        r = np.where(norm < 0.5, 0, np.where(norm < 0.75, (255 * 4 * (norm - 0.5)), 255)).astype(np.uint8)
        g = np.where(norm < 0.25, (255 * 4 * norm), np.where(norm < 0.75, 255, (255 * 4 * (1 - norm)))).astype(np.uint8)
        b = np.where(norm < 0.25, 255, np.where(norm < 0.5, (255 * 4 * (0.5 - norm)), 0)).astype(np.uint8)
        img = np.stack((r, g, b), axis=-1)
        surface = pg.surfarray.make_surface(img)
        return pg.transform.scale(surface, self.grid_size)
        
    def get_velocity_field_img(self) -> pg.Surface:
        
        img = np.zeros((self.grid_size[1], self.grid_size[0], 3), dtype=np.uint8)
        
        #   calculate velocity vectors at cell centers
        u = 0.5 * (self.u[:-1, :] + self.u[1:, :])
        v = 0.5 * (self.v[:, :-1] + self.v[:, 1:])
        vec = np.stack((-v, u))  #  negate v for screen coordinates
        
        #   calculate magnitude
        mag: np.ndarray = np.sqrt(np.sum(vec ** 2, axis=0)) * self.scale
        mag_clipped = np.clip(mag, 0, 2 * self.cell_px * self.scale)
        d = np.where(mag > 0, vec / mag, 0)     #   direction vector
        
        #   draw velocity lines
        steps = np.linspace(0, 1, 50)
        for step in steps:
            step: float
            pos = (self.pos + 0.4 * d * mag_clipped * step).astype(int)
            np.clip(pos, 0, self.num_cells * self.cell_px - 1, out=pos)
            img[pos[1], pos[0]] = (150, 150, 150) if step < 0.7 else (255, 255, 255)
                    
        surface = pg.surfarray.make_surface(img)
        surface.set_colorkey((0, 0, 0))
        return surface