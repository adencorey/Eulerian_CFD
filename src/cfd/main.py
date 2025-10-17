import pygame as pg
from pygame._sdl2.video import Window

import logging

import cfd.utilities.logger as log
from cfd.interface.config import config
from cfd.app import App

def main() -> None:
    
    #   initialise pygame screen
    pg.init()
    #   maximise and no OS manager (minimise/quit buttons)
    screen = pg.display.set_mode((0, 0), pg.RESIZABLE | pg.NOFRAME)
    window = Window.from_display_module()
    window.maximize()
    window.resizable = False
    pg.display.set_caption("Eulerian CFD")
    logger.info("Initialised Pygame")

    #   initialise config
    config.__init__(screen.get_width(), screen.get_height())
    logger.info("Initialised interface config")
    
    app = App(screen)
    app.run()
    
if __name__ == "__main__":
    
    log.init()
    logger = logging.getLogger("cfd.main")
    main()