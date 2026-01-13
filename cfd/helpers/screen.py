import numpy as np

from cfd.interface.config import config

def get_grid(row, col) -> tuple[int, int]:
    """returns suitable position for widgets in specific 'row and 'columns'"""
    
    x_off, y_off = 0.04 * config.width, 0.02 * config.width
    return tuple(np.round((row * config.width / 30 + x_off, col * config.height / 30 + y_off)).tolist())

TITLE_POS = get_grid(1, 3)
LARGE_WIDGET = int(0.2 * config.width), int(0.05 * config.height)
SB_DIM = int(0.15 * config.width), int(0.01 * config.height)