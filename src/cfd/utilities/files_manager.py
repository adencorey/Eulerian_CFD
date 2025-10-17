import os
import json
import logging

from cfd.utilities.time import get_now

log = logging.getLogger(__name__)


SAVES_PATH = os.path.dirname(os.path.join("local", "saves"))
os.makedirs(SAVES_PATH, exist_ok=True)

def create_json(filepath, content:dict) -> True | False:

    try:
        with open(filepath, "x") as file:
            json.dump(content, file, indent=4)
            log.info(f"Successfully created {filepath}")
            return True
    except FileExistsError as e:
        log.error(f"{filepath} already exists ({e})")
    except PermissionError as e:
        log.error(f"Cannot write to file, please enable permision to read/write files ({e})")
    return False
        

def load_json(filepath) -> dict:
    
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except ValueError as e:
        log.error(f"Cannot read from {filepath}, json may be corrupted ({e})")
    except PermissionError as e:
        log.error(f"File cannot be read, please enable permission to read/write files ({e})")
    except Exception as e:
        log.error(f"An error has occured when reading from {filepath} ({e})")
    return False

    
def create_project(name:str, gravity:int) -> None:
    """creates new project directory"""
    
    def create_dir(name:str, gravity:int) -> True | False:
        
        filepath = os.path.join(SAVES_PATH, name)
        options = {
            "gravity": gravity
        }
        metadata = {
            "date_created": get_now(sec=False),
            "last_opened": get_now(sec=False)
        }
        
        try:
            log.debug("Creating new project directory...")
            os.makedirs(filepath)
            create_json(os.path.join(filepath, "options.json"), options)
            create_json(os.path.join(filepath, "metadata.json"), metadata)
            return True               
        
        except FileExistsError:
            log.warning(f"Project name {name} has already been taken")
            return False
        
    if not name: name = "New Project"
    if create_dir(name, gravity): return
    counter = 1
    while True:
        if not create_dir(f"{name} ({counter})", gravity):
            counter += 1
        else:
            break
        
def scan_projects() -> list[dict]:
    """scans all saved projects"""
    
    projects: list[dict] = []
    for entry in os.scandir(SAVES_PATH):
        if not entry.is_dir(): continue     #   skip if not a folder
        
        data = {
            "name": entry.name,
            "path": entry.path,
            "options": {},
            "metadata": {}
        }
        
        for item in os.scandir(entry.path):
            if not item.is_file(): continue
            
            #   read and load project files
            match item.name:
                case "metadata.json":
                    content = load_json(item.path)
                    if not content: continue
                    data["metadata"] = content
                    
                case "options.json": pass
                case _: continue
        
        if data["options"]: projects.append(data)
    return projects