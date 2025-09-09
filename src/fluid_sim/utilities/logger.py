import os
import logging

#   initialise logging
def init() -> None:
    
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-7s] %(name)-40s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("./logs/fluid_sim.log", "w"),
            logging.StreamHandler()
        ]
    )