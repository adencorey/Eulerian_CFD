import numpy as np
import pygame as pg

from cfd.helpers.files import Project
from cfd.interface.config import config
from cfd.settings.manager import settings
from cfd.simulation.algorithms import *


class Grid:
    
    def __init__(self, project: Project) -> None:
        
        self.dt = 1 / settings.fps
        self.num_cells =     int(project.options["resolution"])
        self.scale = (self.num_cells - 2) / 32
        self.env_length = 10                    #   10 meters
        self.cell_size = self.env_length / (self.num_cells - 2)
        
        self.cell_px = int(0.95 * config.height // self.num_cells)
        self.dim = (self.num_cells * self.cell_px * np.ones(2)).astype(np.uint16)
        self.surf = pg.Surface(self.dim)
        self.rect = self.surf.get_rect(bottomright=np.array((config.width, config.height)) - int((0.98 * config.height - self.dim[1]) / 2) * np.ones(2))
        
        # screen coord of cell centers
        side = np.arange(self.num_cells) * self.cell_px + self.cell_px // 2
        x, y = np.meshgrid(side, side)
        self.pos = np.stack((x, y))
        
        self.density = 1
        COLLOCATED_GRID = [self.num_cells, self.num_cells]
        
        #   wall cells  (1 - valid cell; 0 - wall cell)
        self.w = np.ones(COLLOCATED_GRID, dtype=np.uint8)
        self.w[1:-1, 1] = 0
        self.w[1:-1, -2] = 0
        self.w[1, 2:-2] = 0
        self.w[-2, 2:-2] = 0
        
        #   velocity field
        self.u = np.zeros((self.num_cells, self.num_cells + 1), dtype=np.float64)
        self.v = np.zeros((self.num_cells + 1, self.num_cells), dtype=np.float64)
        self.nu = np.zeros((self.num_cells, self.num_cells + 1), dtype=np.float64)
        self.nv = np.zeros((self.num_cells + 1, self.num_cells), dtype=np.float64)
        
        #   divergence field
        self.div = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        
        #  smoke field
        self.s = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        self.ns = np.zeros(COLLOCATED_GRID, dtype=np.float64)
        
        #   pressure field
        self.p = np.zeros(COLLOCATED_GRID, dtype=np.float64)
    
    
    #   ==========[ UTILITIES ]==========        
    def hovered_cell(self, mouse_pos) -> tuple[int, int] | None:
        idx = None
        if self.rect.collidepoint(mouse_pos):
            idx = (np.array(mouse_pos) - np.array(self.rect.topleft)) // self.cell_px
            idx = None if np.any((idx < 0) | (idx >= self.num_cells)) else tuple(np.flip(idx).tolist())
        return idx
    
    def shrink_field(self, arr: np.ndarray) -> np.ndarray:

        side = arr.shape[0]
        if side <= 64 or side % 2 == 1: return arr
        arr = arr.reshape(side // 2, 2, side).sum(axis=1)               #   merge every two rows by summing their respective column values  (shrink vertically)
        arr = arr.reshape(side // 2, side // 2, 2).sum(axis=-1)         #   for every new rows, sum every two values into one               (shrink horizontally)
        return self.shrink_field(0.25 * arr)
    
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
    
    #   --ARCHIVE-- BAD DRAWING FUNCTIONS
    """
    def draw_smoke(self, screen: pg.Surface) -> None:
        for row in range(len(self.s)):
            for col in range(len(self.s[row])):
                s = self.s[row, col]
                if settings.theme_name == "Light": s = 1 - s
                c = int(255 * s)
                rect = pg.Rect((0, 0), (self.cell_px, self.cell_px))
                rect.center = self.pos[:, row, col]
                pg.draw.rect(self.surf, [c] * 3, rect)
        screen.blit(self.surf, self.rect)
        
    def draw_vel(self, screen: pg.Surface) -> None:
        k = self.cell_px / self.cell_size
        max_len = self.cell_px * 2
        for row in range(len(self.s)):
            for col in range(len(self.s[row])):
                u = 0.5 * (self.u[row, col] + self.u[row, col + 1]) * k
                v = 0.5 * (self.v[row, col] + self.v[row + 1, col]) * k
                mag: float = (u ** 2 + v ** 2) ** 0.5
                line_len: float = mag if mag <= max_len else max_len
                start = self.pos[:, row, col]
                end = start + (np.array((u, -v)) / mag * line_len).astype(int)
                pg.draw.line(self.surf, (128, 128, 128), start, end, self.cell_px // 5)
        screen.blit(self.surf, self.rect)
    """
    
    def get_walls_field_img(self, img:np.ndarray) -> None:

        is_wall = self.w == 0
        img[is_wall] = config.hvr_clr
    
    def get_smoke_field_img(self, img:np.ndarray) -> None:
        
        s = self.s.copy().T
        if settings.theme_name == "light":
            s = 1 - s
        c = (255 * s).astype(np.uint8)
        img[:, :] = np.stack([c] * 3, axis=-1)
    
    def get_divergence_field_img(self, img:np.ndarray) -> None:
        div = np.clip(self.div, -5, 5).T
        norm = div / 5
        r = (255 * np.where(norm > 0, norm, 0)).astype(np.uint8)        #   red if outflow
        g = np.zeros_like(norm)
        b = (255 * np.where(norm < 0, -norm, 0)).astype(np.uint8)       #   blue if inflow
        img[:, :] = np.stack((r, g, b), axis=-1)
    
    def get_pressure_field_img(self, img, smoke_only=False) -> None:

        p = self.p.T
        max_p = 5_000 * self.density
        np.clip(p, -max_p, max_p, out=p)
        norm = 0.5 * (p / max_p) + 0.5
                
        #   jet colourmap (rainbow gradient)
        r = np.where(norm < 0.5, 0, np.where(norm < 0.75, (255 * 4 * (norm - 0.5)), 255))
        g = np.where(norm < 0.25, (255 * 4 * norm), np.where(norm < 0.75, 255, (255 * 4 * (1 - norm))))
        b = np.where(norm < 0.25, 255, np.where(norm < 0.5, (255 * 4 * (0.5 - norm)), 0))
        weight = np.clip(1.5 * self.s, 0, 1).T if smoke_only else np.ones_like(p)
        img[:, :] = np.stack((r, g, b) * weight, axis=-1).astype(np.uint8)

    def get_velocity_field_img(self, img:np.ndarray) -> None:
        
        u = 0.5 * (self.u[:, :-1] + self.u[:, 1:])
        v = 0.5 * (self.v[:-1, :] + self.v[1:, :])

        nu, nv = self.shrink_field(u).T, self.shrink_field(v).T
        factor = u.shape[0] / nu.shape[0]
        vel = np.stack((-nv, nu)) / self.cell_size * self.cell_px  #  negate v for screen coordinates
        
        mag = np.zeros_like(nu)
        mag[1:-1, 1:-1] = np.sqrt(np.sum(vel[:, 1:-1, 1:-1] ** 2, axis=0))
        mag_clipped = np.clip(mag, 0, self.cell_px * 1.25 * factor)
        
        is_mag = mag > 0
        d = np.zeros_like(vel)
        d[:, is_mag] = vel[:, is_mag] / mag[is_mag]     #   get direction vector where mag > 0
        
        #   draw velocity lines
        steps = np.linspace(0, 1, 20)
        position = np.array((self.shrink_field(self.pos[0]), self.shrink_field(self.pos[1])))
        for step in steps:
            pos = (position[:, is_mag] + mag_clipped[is_mag] * d[:, is_mag] * step).astype(int)
            valid = (0 < pos[0]) & (pos[0] < self.dim[0]) & (0 < pos[1]) & (pos[1] < self.dim[1])
            colour = (128, 128, 128) if step < 0.7 else (0, 128, 128)
            img[pos[1][valid], pos[0][valid]] = colour