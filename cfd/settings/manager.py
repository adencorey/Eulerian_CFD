import os
import json
import logging

from cfd.settings.themes import THEME

log = logging.getLogger(__name__)

class Settings:

    def __init__(self, theme_name="dark", fps=60, show_fps=False, iterator=50, sor_weight=1.6) -> None:
        
        os.makedirs(os.path.dirname(self.path), exist_ok=True)  #   make the directory /local/settings.json
        self.theme_name = theme_name
        self.fps = fps
        self.show_fps = show_fps
        self.iterator = iterator
        self.sor_weight = sor_weight
        self.load()
    
    @property
    def path(self):
        return os.path.join("local", "settings.json")
    @property
    def theme(self):
        return THEME[self.theme_name]
        
    def save(self) -> True | False:
        """save current settings to json file"""
        
        try:
            with open(self.path, "w") as file:
                json.dump(self.__dict__, file, indent=4)    #   turns all attributes into a dictionary and store into settings.json
                log.info("Settings successfully saved")
                return True
            
        except PermissionError as e:
            log.warning(f"File cannot be written, please enable permission to read/write files ({e})")

        except Exception as e:
            log.warning(f"An error has occured when saving settings ({e})")
        return False
        
    def load(self) -> None:
        """load settings from json file"""
        
        #   if settings.json exists
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as file:
                    data: dict[str, any] = json.load(file)  #   read settings.json as a dictionary
                    for key, value in data.items():
                        setattr(self, key, value)           #   set attribute for all in data
            
            except ValueError as e:
                log.warning(f"Failed to read file, file may be corrupted ({e}) ")
        else:
            log.debug("Settings file not found, using default settings")
settings = Settings()


#   ==========[ SETTINGS PRESETS ]==========
DEFAULT = Settings(
    theme_name="dark",
    fps=60,
    show_fps=False,
    iterator=50,
    sor_weight=1.6
)

PERFORMANCE = Settings(
    theme_name="dark",
    fps=30,
    show_fps=True,
    iterator=30,
    sor_weight=1.8
)

ULTRA = Settings(
    theme_name="dark",
    fps=120,
    show_fps=False,
    iterator=100,
    sor_weight=1.4
)