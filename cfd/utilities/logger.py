import os
import logging

#   initialise logging
def init() -> None:
    
    os.makedirs("logs", exist_ok=True)  #   create logs dir if not already
    logging.basicConfig(
        level=logging.DEBUG,    #   shows debug messages and up
        format="%(asctime)s [%(levelname)-7s] %(name)-40s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("./logs/cfd.log", "w"),   #   save in file
            logging.StreamHandler()                             #   print out in console
        ]
    )