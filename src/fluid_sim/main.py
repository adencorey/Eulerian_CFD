import pygame as pg

import logging

import fluid_sim.logger as log
from fluid_sim.app import App
from fluid_sim.settings import Settings

def main() -> None:
    
    #   initialise pygame screen
    pg.init()
    #   set fullscreen and no OS manager (minimise/quit buttons)
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN | pg.NOFRAME)
    pg.display.set_caption("Eulerian CFD")
    logger.info("Initialised Pygame")
    
    #   load user settings
    settings = Settings()
    
    
    app = App(screen, settings=settings)
    app.run()
    
if __name__ == "__main__":
    
    log.init()
    logger = logging.getLogger("fluid_sim.main")
    main()