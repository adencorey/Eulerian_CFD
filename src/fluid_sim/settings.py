import os
import json
import logging

log = logging.getLogger(__name__)

#   ==========[ THEMES ]==========
class Theme:
    
    def __init__(self, background, main, hover):
        
        self.background = background
        self.main = main
        self.hover = hover
    
THEME = {
    
    "light": Theme(
        background=(255, 255, 255),
        main=(0, 0, 0),
        hover=(200, 200, 200)
    ),
    "dark": Theme(
        background=(50, 50, 50),
        main=(220, 220, 220),
        hover=(100, 100, 100)
    )
}


#   ==========[ SETTINGS ]==========
class Settings:

    def __init__(self, theme_name="dark", fps=60):
        
        self.theme_name = theme_name
        self.fps = fps
        self.load()
    
    #   method that acts like an attribute, returns the actual theme class
    @property
    def path(self):
        return os.path.join("local", "settings.json")
    @property
    def theme(self):
        return THEME[self.theme_name]
        
    def save(self):
        
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)  #   make the directory /local/settings.json
            with open(self.path, "w") as file:
                json.dump(self.__dict__, file, indent=4)    #   turns all attributes into a dictionary and store into settings.json
                log.info("Settings successfully saved")
                return True
            
        except PermissionError as e:
            log.warning(f"File cannot be written, please enable permission to read/write files ({e})")
            return False
        
    def load(self):
        
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
        
#   presets
DEFAULT = Settings(
    theme_name="dark",
    fps=60
)

PERFORMANCE = Settings(
    theme_name="dark",
    fps=30
)