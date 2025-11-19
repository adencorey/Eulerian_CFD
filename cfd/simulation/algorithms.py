import numpy as np
from numba import njit, prange

#   ==========[ BOUNDARY CONDITIONS ]==========
@njit("void(float64[:, :], float64[:, :], float64[:, :])", cache=True)
def ghost_cells_boundary_check(u:np.ndarray[np.float64], v:np.ndarray[np.float64], s:np.ndarray[np.float64]) -> None:
    u[0, :] = u[-1, :] = u[:, 0] = u[:, -1] = 0
    v[:, 0] = v[:, -1] = v[:, 0] = v[:, -1] = 0
    s[0, :] = s[-1, :] = s[:, 0] = s[:, -1] = 0

@njit("void(uint16, uint8[:, :], float64[:, :], float64[:, :], float64[:, :])", cache=True, parallel=True)
def free_slip_boundary_check(num_cells:int, w:np.ndarray[np.uint8], u:np.ndarray[np.float64], v:np.ndarray[np.float64], s:np.ndarray[np.float64]) -> None:
    """set velocity to 0 at wall cells"""
    
    for i in prange(1, num_cells):
        for j in prange(1, num_cells - 1):
            if w[i, j] == 0 or w[i-1, j] == 0:
                u[i, j] = 0
    
    for i in prange(1, num_cells - 1):
        for j in prange(1, num_cells):
            if w[i, j] == 0 or w[i, j-1] == 0:
                v[i, j] = 0
    
    for i in prange(num_cells):
        for j in prange(num_cells):
            if w[i, j] == 0: s[i, j] = 0
                
            
#   ==========[ PROJECTION ]==========
@njit("void(uint16, float32, uint8[:, :], float64[:, :], float64[:, :], float64[:, :])", cache=True, parallel=True, fastmath=True)
def get_divergence_field(num_cells:int, cell_size:float, w:np.ndarray[np.uint8], u:np.ndarray[np.float64], v:np.ndarray[np.float64], div:np.ndarray[np.float64]) -> None:
    """get total inflow/outflow of all cells divided by cell size"""

    for i in prange(1, num_cells - 1):
        for j in prange(1, num_cells - 1):
            div[i, j] = (u[i+1, j] - u[i, j] + v[i, j] - v[i, j+1]) / cell_size if w[i, j] == 1 else 0

@njit("float64[:, :](float32, uint16, float32, float32, uint8[:, :], float64[:, :], uint16, float32)", cache=True, fastmath=True)
def poisson_pressure_solve(dt:float, num_cells:int, cell_size_sq:float, density:float, w:np.ndarray[np.uint8], div:np.ndarray[np.float64], iter:int, sor_weight:float) -> np.ndarray[np.float64, np.float64]:
    """solves pressure field iteratively (Gauss-Seidel) using Poisson's pressure equation"""
    
    p = np.zeros((num_cells, num_cells), dtype=np.float64)
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
                
                #   new pressure = (sum of adj pressures - (density * cell size ** 2 * velocity flux / dt)) / num of adj cells
                new_p = (((p[i-1, j] * w_l) + (p[i+1, j] * w_r) + (p[i, j-1] * w_t) + (p[i, j+1] * w_b)) - cell_size_sq * density * div[i, j] / dt) / num_fluid_cells
                p[i, j] += (new_p - p[i, j]) * sor_weight       #   successive over-relaxation    
    return p
                

@njit("void(float32, uint16, float32, float32, uint8[:, :], float64[:, :], float64[:, :], float64[:, :])", cache=True, parallel=True)
def pressure_projection(dt:float, num_cells:int, cell_size:float, density:float, w:np.ndarray[np.uint8], p:np.ndarray[np.float64], u:np.ndarray[np.float64], v:np.ndarray[np.float64]) -> None:
    """
    clears out divergence by calculating pressure field and finding pressure gradient, since curl of the pressure gradient field = 0 we also found curl-free field\n
    according to Helmholtz's decomposition theorem, any field = divergence-free part + curl-free part\n
    rearrange to get: divergence-free = field - curl-free
    """
    k = dt / (cell_size * density)
    #   update horizontal velocity
    for i in prange(1, num_cells):
        for j in prange(1, num_cells - 1):
            wall_u = w[i, j] == 0 or w[i-1, j] == 0            
            if not wall_u:
                dpdx = p[i, j] - p[i-1, j]   #   find pressure gradient
                u[i, j] -= k * dpdx
            else:
                u[i, j] = 0            
                
    #   update vertical velocity
    for i in prange(1, num_cells - 1):
        for j in prange(1, num_cells):            
            wall_v = w[i, j] == 0 or w[i, j-1] == 0
            if not wall_v:
                dpdy = p[i, j] - p[i, j-1]   #   find pressure gradient
                v[i, j] -= k * -dpdy         #  negate for screen coords
            else:
                v[i, j] = 0

"""
29/10: pressure projection exploded
fixed: wrong code (k = cell_size / dt and top - center)
blew up again: wrong code (add press grad in y bc of screen coord)
"""

#   ==========[ ADVECTION ]==========
@njit("float64(float64[:, :], int16[:], float64[:])", cache=True, inline="always")
def bilerp(field:np.ndarray[np.float64], floor:tuple[np.int16], fract:tuple[np.float64]) -> np.float64:
    """
    bilinear interpolate between 4 points\n
    floor - index of topleft
    fract - proportion from left to right, top to bottom
    """
    i, j = floor
    fi, fj = fract
    t = (1 - fi) * field[i, j] + fi * field[i+1, j]         #   lerp top left and top right
    b = (1 - fi) * field[i, j+1] + fi * field[i+1, j+1]     #   lerp bottom left and bottom right
    return (1 - fj) * t + fj * b                            #   lerp top and bottom


@njit("Tuple((int16, float64))(uint16, uint16, float64)", cache=True, inline="always")
def clamp_index(num_cells:int, floor:np.int16, fract:np.float64) -> tuple[np.int16, np.float64]:
    """clamp index and proportion to staggered grid format"""
    if fract < 0.5:
        floor -= 1
        fract += 0.5
    else:
        fract -= 0.5
    if floor < 0: floor = 1
    elif floor >= num_cells: floor = num_cells - 1
    return floor, fract

@njit("Tuple((int16[:], float64[:]))(float64[:])", cache=True, inline="always")
def split_index(idx:np.ndarray[np.float64]) -> tuple[np.ndarray[np.int16], np.ndarray[np.float64]]:
    """splits index into floor part and fractional part"""
    
    i, j = idx
    floor = np.array((int(i), int(j)), dtype=np.int16)
    fract = idx - floor
    return floor, fract
    

@njit("float64[:](uint16, float64[:, :], float64[:, :], float64[:])", cache=True, inline="always")
def get_velocity_at_pos(num_cells:int, u:np.ndarray[np.float64], v:np.ndarray[np.float64], idx:np.ndarray[np.float64]) -> np.ndarray[np.float64, np.float64]:
    """get velocity at given position where vertical velocity is negated for screen coordinates"""
    
    """
    i, j = np.floor(idx).astype(np.uint16)
    fi, fj = idx - np.array((i, j))
    i, fi = clamp_index(i, fi)
    j, fj = clamp_index(j, fj)
    x_vel = bilerp(u, (i, j), (fi, fj))
    y_vel = bilerp(v, (i, j), (fi, fj))
    
    problem: u and v are stored in diff pos, so need to clamp separately
    """
    (ui, vj), (fui, fvj) = split_index(idx)
    uj, fuj = clamp_index(num_cells + 1, vj, fvj)
    vi, fvi = clamp_index(num_cells + 1, ui, fui)
    x_vel = bilerp(u, (ui, uj), (fui, fuj))
    y_vel = bilerp(v, (vi, vj), (fvi, fvj))
    return np.array((x_vel, -y_vel))        #   negate y for screen coord

@njit("float64(uint16, float64[:, :], float64[:])", cache=True, inline="always")
def get_u_at_pos(num_cells:int, u:np.ndarray[np.float64], idx:np.ndarray[np.float64]) -> np.float64:
    """get horizontal velocity at given position"""
    
    (i, j), (fi, fj) = split_index(idx)
    j, fj = clamp_index(num_cells + 1, j, fj)
    return bilerp(u, (i, j), (fi, fj))

@njit("float64(uint16, float64[:, :], float64[:])", cache=True, inline="always")
def get_v_at_pos(num_cells:int, v:np.ndarray[np.float64], idx:np.ndarray[np.float64]) -> np.float64:
    """get vertical velocity at given position"""
    
    (i, j), (fi, fj) = split_index(idx)
    i, fi = clamp_index(num_cells + 1, i, fi)
    return bilerp(v, (i, j), (fi, fj))

@njit("float64(uint16, float64[:, :], float64[:])", cache=True, inline="always")
def get_density_at_pos(num_cells:int, s:np.ndarray[np.float64], idx:np.ndarray[np.float64]) -> np.float64:
    """get smoke density at a given position"""

    (i, j), (fi, fj) = split_index(idx)
    i, fi = clamp_index(num_cells, i, fi)
    j, fj = clamp_index(num_cells, j, fj)
    return bilerp(s, (i, j), (fi, fj))

@njit("void(float32, float32, uint16, uint8[:, :], float64[:, :], float64[:, :], float64[:, :], float64[:, :])", cache=True, parallel=True, fastmath=True)
def semi_lagrangian_advect_velocity(dt:float, cell_size:float, num_cells:int, w:np.ndarray[np.uint8], u:np.ndarray[np.float64], v:np.ndarray[np.float64], nu:np.ndarray[np.float64], nv:np.ndarray[np.float64]) -> None:
    """calculate new velocity by backtracking by dt and bilinear interpolate between 4 cells"""
    
    #   advect horizontal velocities
    for i in prange(1, num_cells):
        for j in prange(1, num_cells - 1):
            if w[i, j] == 0 or w[i-1, j] == 0: 
                nu[i, j] = 0
                continue
            
            #   get velocity at vertical cell face
            old_idx = np.array((i, j + 0.5))
            old_vel = get_velocity_at_pos(num_cells, u, v, old_idx) / cell_size
            
            #   backtrack using velocity found
            new_idx = old_idx - old_vel * dt
            nu[i, j] = get_u_at_pos(num_cells, u, new_idx)
    
    #   advect vertical velocities
    for i in prange(1, num_cells - 1):
        for j in range(1, num_cells):
            if w[i, j] == 0 or w[i, j-1] == 0: 
                nv[i, j] = 0
                continue
            
            #   get velocity at horizontal cell face
            old_idx = np.array((i + 0.5, j))
            old_vel = get_velocity_at_pos(num_cells, u, v, old_idx) / cell_size
            
            #   backtrack
            new_idx = old_idx - old_vel * dt
            nv[i, j] = get_v_at_pos(num_cells, v, new_idx)

"""
31st Oct: First attempt, seems like we have got a syntax error, numba doesn't allow astype(int) so I changed it
Second attempt, making a mess in divergence and making pointy shape (unphysical). Seems like y vel is wrong bc of screen coord sys
Thrid attempt, works fine horizontally, but it wobbles between +/- y, and they dont like to move up or down. Problem is I forgot to negate velocity when assigning real one

div on left side, bad boundary checking, now fixed but advect step access index out of bounds so need to clamp
now program breaks after 1 sec
"""

@njit("void(float32, float32, uint16, uint8[:, :], float64[:, :], float64[:, :], float64[:, :],  float64[:, :])", cache=True, parallel=True, fastmath=True)
def semi_lagrangian_advect_smoke(dt:float, cell_size:float, num_cells:int, w:np.ndarray[np.uint8], s:np.ndarray[np.float64], ns:np.ndarray[np.float64], u:np.ndarray[np.float64], v:np.ndarray[np.float64]) -> None:
    """calculate new smoke density by backtracking by dt and bilinear interpolate between 4 cells"""
    
    for i in prange(1, num_cells - 1):
        for j in prange(1, num_cells - 1):
            if w[i, j] == 0: 
                ns[i, j] = 0
                continue
            
            #   get velocity at cell center
            old_idx = (np.array((i, j))) + 0.5
            old_vel = get_velocity_at_pos(num_cells, u, v, old_idx) / cell_size

            #   backtrack
            new_idx = old_idx - old_vel * dt
            ns[i, j] = get_density_at_pos(num_cells, s, new_idx)

"""
31st oct: first attempt, even though velocity is 0 density is moving to topleft, seems like get_density_at_pos() is a little bit off when same pos is input
Turns out I forgot to clamp index to center of cell, I was interpolating using the topleft corner
"""



"""
31st Oct: Tries to build a wind tunnel, albeit the high neg divergence and high overall pressuree. Vortex shredding can be shown.
Seems like boundary check is done badly, mass cannot leave system and hence compresses, and pressure rises to resist inflow.
changed to only copy interior values if outflow else stay as it is
"""