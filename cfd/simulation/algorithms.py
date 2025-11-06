import numpy as np
from numba import njit, prange

#   ==========[ UTILITIES ]==========
@njit(cache=True)
def inbound_idx(num_cells:int, i, j) -> True | False:
    return i >= 0 and i < num_cells and j >= 0 and j < num_cells 

#   ==========[ BOUNDARY CONDITIONS ]==========
def ghost_cells_boundary_check(u:np.ndarray, v:np.ndarray):
    """copy neighbouring cells at boundary so fluids flow out of screen"""
    
    for vel in [u, v]:
        vel[0, :] = np.where(vel[1, :] >= 0, vel[0, :], vel[1, :])
        vel[-1, :] = np.where(vel[-2, :] <= 0, vel[-1, :], vel[-2, :])
        vel[:, 0] = np.where(vel[:, 1] <= 0, vel[:, 0], vel[:, 1])
        vel[:, -1] = np.where(vel[:, -2] >= 0, vel[:, -1], vel[:, -2])        

@njit(parallel=True, cache=True)
def free_slip_boundary_check(num_cells:int, w:np.ndarray, u:np.ndarray, v:np.ndarray) -> None:
    """set velocity to 0 at wall cells"""
    
    for i in prange(1, num_cells):
        for j in range(1, num_cells - 1):
            if w[i, j] == 0 or w[i-1, j] == 0:
                u[i, j] = 0
    
    for i in prange(1, num_cells - 1):
        for j in range(1, num_cells):
            if w[i, j] == 0 or w[i, j-1] == 0:
                v[i, j] = 0                
                
            
#   ==========[ PROJECTION ]==========
@njit(parallel=True, cache=True)
def get_divergence_field(num_cells, cell_size:int, w:np.ndarray, u:np.ndarray, v:np.ndarray) -> np.ndarray:
    """get total inflow/outflow of all cells divided by cell size"""
    
    div = np.zeros((num_cells, num_cells), dtype=np.float64)
    for i in prange(1, num_cells - 1):
        for j in range(1, num_cells - 1):
            if w[i, j] == 0: continue
            
            u_l = u[i, j]
            u_r = u[i+1, j]
            v_t = v[i, j]
            v_b = v[i, j+1]
            u_grad = (u_r - u_l) / cell_size
            v_grad = (v_t - v_b) / cell_size
            div[i, j] = u_grad + v_grad
            
    return div    

@njit(parallel=True, cache=True)
def poisson_pressure_solve(dt:float, num_cells:int, cell_size:int, w:np.ndarray, div:np.ndarray, iter:int=30, sor_weight:float=1.7) -> np.ndarray:
    """solves pressure field iteratively (Gauss-Seidel) using Poisson's pressure equation"""
    
    p = np.zeros((num_cells, num_cells), dtype=np.float64)
    cell_size_sq = cell_size ** 2
    for _ in range(iter):
        for i in range(1, num_cells - 1):
            for j in range(1, num_cells - 1):
                w_l = w[i-1, j]
                w_r = w[i+1, j]
                w_t = w[i, j-1]
                w_b = w[i, j+1]
                num_fluid_cells = w_l + w_r + w_t + w_b
                if w[i, j] == 0 or num_fluid_cells == 0:
                    p[i, j] = 0
                    continue
                
                p_l = p[i-1, j] * w_l
                p_r = p[i+1, j] * w_r
                p_t = p[i, j-1] * w_t
                p_b = p[i, j+1] * w_b
                adj_pressure_sum = p_l + p_r + p_t + p_b
                
                new_p = (adj_pressure_sum - sor_weight * cell_size_sq * div[i, j] / dt) / num_fluid_cells
                p[i, j] += (new_p - p[i, j]) * sor_weight
    return p
                

@njit(parallel=True, cache=True)
def pressure_projection(dt:float, num_cells:int, cell_size:int, w:np.ndarray, p:np.ndarray, u:np.ndarray, v:np.ndarray) -> None:
    """
    clears out divergence by calculating pressure field and finding pressure gradient, since curl of the pressure gradient field = 0 we also found curl-free field\n
    according to Helmholtz's decomposition theorem, any field = divergence-free part + curl-free part\n
    rearrange to get: divergence-free = field - curl-free
    """
    k = dt / cell_size
    
    #   update horizontal velocity
    for i in prange(1, num_cells):
        for j in range(1, num_cells - 1):
            wall_u = w[i, j] == 0 or w[i-1, j] == 0            
            if not wall_u:
                dpdx = p[i, j] - p[i-1, j]   #   find pressure gradient
                u[i, j] -= k * dpdx
            else:
                u[i, j] = 0            
                
    #   update vertical velocity
    for i in prange(1, num_cells - 1):
        for j in range(1, num_cells):            
            wall_v = w[i, j] == 0 or w[i, j-1] == 0
            if not wall_v:
                dpdy = p[i, j] - p[i, j-1]   #   find pressure gradient
                v[i, j] += k * dpdy
            else:
                v[i, j] = 0

"""
29/10: pressure projection exploded
fixed: wrong code (k = cell_size / dt and top - center)
blew up again: wrong code (add press grad in y bc of screen coord)
"""          

#   ==========[ ADVECTION ]==========
@njit(cache=True)
def lerp(a, b, k) -> np.float64:
    """linear interpolate between a and b, k is the proportion from a to b
    """
    return (1 - k) * a + k * b

@njit(cache=True)
def bilerp(field:np.ndarray, floor:tuple[int, int], fract:tuple[float, float]) -> np.float64:
    """
    bilinear interpolate between 4 points\n
    floor - index of topleft
    fract - proportion from left to right, top to bottom
    """
    i, j = floor
    fi, fj = fract
    t = lerp(field[i, j], field[i + 1, j], fi)              #   lerp top left and top right
    b = lerp(field[i, j + 1], field[i + 1, j + 1], fi)      #   lerp bottom left and bottom right
    return lerp(t, b, fj)                                   #   lerp top and bottom


@njit(cache=True)
def clamp_index(floor, fract) -> tuple[int, float]:
    """clamp index and proportion to staggered grid format"""
    if fract < 0.5:
        floor -= 1
        fract += 0.5
    else:
        fract -= 0.5
    return floor, fract

@njit(cache=True)
def get_velocity_at_pos(u:np.ndarray, v:np.ndarray, idx:np.ndarray) -> np.ndarray:
    """get velocity at a given position"""
    
    """
    i, j = np.floor(idx).astype(np.uint16)
    fi, fj = idx - np.array((i, j))
    i, fi = clamp_index(i, fi)
    j, fj = clamp_index(j, fj)
    x_vel = bilerp(u, (i, j), (fi, fj))
    y_vel = bilerp(v, (i, j), (fi, fj))
    
    problem: u and v are stored in diff pos, so need to clamp separately
    """
    ui, vj = np.floor(idx).astype(np.uint16)
    fui, fvj = idx - np.array((ui, vj))
    uj, fuj = clamp_index(vj, fvj)
    vi, fvi = clamp_index(ui, fui)
    x_vel = bilerp(u, (ui, uj), (fui, fuj))
    y_vel = bilerp(v, (vi, vj), (fvi, fvj))
    return np.array((x_vel, -y_vel))        #   negate y for screen coord

@njit(cache=True)
def get_density_at_pos(s:np.ndarray, idx:np.ndarray) -> np.float64:
    """get smoke density at a given position"""
    
    #idx = pos / cell_px
    i, j = int(idx[0]), int(idx[1])
    fi, fj = idx - np.array((i, j))
    i, fi = clamp_index(i, fi)
    j, fj = clamp_index(j, fj)
    return bilerp(s, (i, j), (fi, fj))

@njit(parallel=True, cache=True)
def semi_lagrangian_advect_velocity(dt:float, cell_px:int, num_cells:int, w:np.ndarray, u:np.ndarray, v:np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """calculate new velocity by backtracking by dt and bilinear interpolate between 4 cells"""
    
    nu = np.zeros_like(u)
    nv = np.zeros_like(v)
    
    #   advect horizontal velocities
    for i in prange(1, num_cells):
        for j in range(1, num_cells - 1):
            if w[i, j] == 0 or w[i-1, j] == 0: continue
            
            #   get velocity at vertical cell face
            old_idx = np.array((i, j)) + np.array((0, 0.5))
            old_vel = get_velocity_at_pos(u, v, old_idx) / cell_px
            
            #   backtrack using velocity found
            new_idx = old_idx - old_vel * dt
            nu[i, j] = get_velocity_at_pos(u, v, new_idx)[0]
    
    #   advect vertical velocities
    for i in prange(1, num_cells - 1):
        for j in range(1, num_cells):
            if w[i, j] == 0 or w[i, j-1] == 0: continue
            
            #   get velocity at horizontal cell face
            old_idx = np.array((i, j)) + np.array((0.5, 0))
            old_vel = get_velocity_at_pos(u, v, old_idx) / cell_px
            
            #   backtrack
            new_idx = old_idx - old_vel * dt
            nv[i, j] = -get_velocity_at_pos(u, v, new_idx)[1]
    
    return nu, nv

"""
31st Oct: First attempt, seems like we have got a syntax error, numba doesn't allow astype(int) so I changed it
Second attempt, making a mess in divergence and making pointy shape (unphysical). Seems like y vel is wrong bc of screen coord sys
Thrid attempt, works fine horizontally, but it wobbles between +/- y, and they dont like to move up or down. Problem is I forgot to negate velocity when assigning real one
"""

@njit(parallel=True, cache=True)
def semi_lagrangian_advect_smoke(dt:float, cell_px:int, num_cells:int, w:np.ndarray, s:np.ndarray, u:np.ndarray, v:np.ndarray) -> np.ndarray:
    
    ns = np.zeros_like(s)
    for i in prange(1, num_cells - 1):
        for j in range(1, num_cells - 1):
            if w[i, j] == 0: continue
            
            #   get velocity at cell center
            old_idx = (np.array((i, j)) + 0.5 * np.ones(2)).astype(np.float64)
            old_vel = get_velocity_at_pos(u, v, old_idx) / cell_px
            
            #   backtrack
            new_idx = old_idx - old_vel * dt
            ns[i, j] = get_density_at_pos(s, new_idx)

    return ns

"""
31st oct: first attempt, even though velocity is 0 density is moving to topleft, seems like get_density_at_pos() is a little bit off when same pos is input
Turns out I forgot to clamp index to center of cell, I was interpolating using the topleft corner
"""



"""
31st Oct: Tries to build a wind tunnel, albeit the high neg divergence and high overall pressuree. Vortex shredding can be shown.
Seems like boundary check is done badly, mass cannot leave system and hence compresses, and pressure rises to resist inflow.
changed to only copy interior values if outflow else stay as it is
"""