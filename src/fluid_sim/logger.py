import logging

#   initialise logging
def init() -> None:
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-10s] %(name)-30s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("fluid_sim.log"),
            logging.StreamHandler()
        ]
    )