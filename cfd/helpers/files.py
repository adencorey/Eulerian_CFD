import os
import json
import logging
import shutil
import numpy as np
from pathlib import Path
from dataclasses import dataclass

from .time import get_now

log = logging.getLogger(__name__)


SAVES_PATH = os.path.join(Path(__file__).parent.parent.parent, "local", "saves")
os.makedirs(SAVES_PATH, exist_ok=True)


#   ==========[ JSON UTIlS ]==========
def create_json(filepath, content:dict) -> True | False:

    try:
        with open(filepath, "x") as file:
            json.dump(content, file, indent=4)
            log.info(f"Successfully created /{filepath}")
            return True
    except FileExistsError as e:
        log.error(f"{filepath} already exists ({e})")
    except PermissionError as e:
        log.error(f"Cannot write to file, please enable permision to write files ({e})")
    except Exception as e:
        log.critical(f"An error has occured when creating /{filepath} ({e})")
    return False
        

def load_json(filepath) -> dict:
    
    try:
        with open(filepath, "r") as file:
            log.debug(f"Successfully loaded /{filepath}")
            return json.load(file)
    except ValueError as e:
        log.error(f"Cannot read from /{filepath}, json may be corrupted ({e})")
    except PermissionError as e:
        log.error(f"I do not have permission to read from /{filepath}, ({e})")
    except Exception as e:
        log.critical(f"An error has occured when loading /{filepath} ({e})")
    return False


def edit_json(filepath, content:dict) -> True | False:
    
    try:
        with open(filepath, "w") as file:
            json.dump(content, file, indent=4)
            log.info(f"Successfully edited /{filepath}")
            return True
    except PermissionError as e:
        log.error(f"Cannot write to file, please enable permision to write files ({e})")
    except Exception as e:
        log.critical(f"An error has occured when creating {filepath} ({e})")
    return False


#   ==========[ NPY UTILS ]==========
def save_npy(path: str, name: str, arr: np.ndarray) -> True | False:
    
    try:
        filepath = os.path.join(path, name)
        np.save(filepath, arr)
        log.info(f"Successfully saved /{filepath}")
        return True
    except PermissionError as e:
        log.error(f"I do not have permission to save to /{filepath}, ({e})")
    return False
    
def load_npy(filepath: str) -> np.ndarray | None:
    
    try:
        array = np.load(filepath)
        log.info(f"Successfully loaded /{filepath}")
        return array
    except ValueError as e:
        log.error(f"Cannot read from /{filepath}, npy may be corrupted ({e})")
    except PermissionError as e:
        log.error(f"I do not have permission to read from /{filepath}, ({e})")
    except FileNotFoundError as e:
        log.error(f"File not found at /{filepath} ({e})")
    return None       


def create_project(name:str, resolution: int, gravity:int) -> None:
    """creates new project directory"""
    
    def create_dir(name:str, resolution: int, gravity:int) -> True | False:
        
        filepath = os.path.join(SAVES_PATH, name)
        options = {
            "resolution": resolution,
            "gravity": gravity
        }
        metadata = {
            "date_created": get_now(sec=False),
            "last_opened": get_now(sec=False)
        }
        
        try:
            os.makedirs(filepath)
            create_json(os.path.join(filepath, "options.json"), options)
            create_json(os.path.join(filepath, "metadata.json"), metadata)
            return True               
        
        except FileExistsError as e:
            log.warning(f"Project name {name} has already been taken, adding counter ({e})")
        except PermissionError as e:
            log.critical(f"File cannot be created, please enable permission to create files ({e})")
        except Exception as e:
            log.critical(f"An error has occured when creating {filepath} ({e})")
        return False
    
    if not name: name = "New Project"
    log.debug(f"Creating project with name {name}...")
    if create_dir(name, resolution, gravity): return
    counter = 1
    while True:
        if not create_dir(f"{name} ({counter})", resolution, gravity):
            counter += 1
        else:
            break
        
def rename_project(old_name:str, new_name:str, counter=1) -> True | False:
    """renames project directory"""
    
    if not new_name: new_name = "New Project"
    log.info(f"Renaming project name from {old_name} to {new_name}...")
    if old_name == new_name: return True
    projects = scan_projects()
    for project in projects:
        if project.name == new_name:
            log.warning(f"Project name {new_name} has already been taken, adding counter")
            if counter != 1:
                name_parts = new_name.split()
                name_parts.pop(-1)
                new_name = " ".join(name_parts)
            return rename_project(old_name, f"{new_name} ({counter})", counter + 1)
    try:
        old_path = os.path.join(SAVES_PATH, old_name)
        new_path = os.path.join(SAVES_PATH, new_name)
        os.rename(old_path, new_path)
        return True

    except PermissionError as e:
        log.critical(f"File cannot be renamed, please enable permission to rename files ({e})")
    except Exception as e:
        log.error(f"An error has occured when renaming {old_path} to {new_path} ({e})")
    return False


def edit_project(name:str, options:dict=None, metadata:dict=None) -> True | False:
    """edits options.json or metadata.json of project"""
    
    log.info(f"Editing project files with name {name}")
    valid = True
    filepath = os.path.join(SAVES_PATH, name)
    if options:
        if not edit_json(os.path.join(filepath, "options.json"), options): 
            valid = False
    if metadata:
        if not edit_json(os.path.join(filepath, "metadata.json"), metadata):
            valid = False
    return valid

def delete_project(name:str) -> True | False:
    """deletes project directory"""
    
    log.info(f"Deleting project with name {name}")
    filepath = os.path.join(SAVES_PATH, name)
    try:
        shutil.rmtree(filepath)
        log.info(f"Successfully deleted project directory with name {name}")
        return True
    except FileNotFoundError as e:
        log.warning(f"Project name {name} not found ({e})")
    except PermissionError as e:
        log.warning(f"Directory cannot be removed, please enable permission to delete files ({e})")
    except Exception as e:
        log.error(f"An error has occured when deleting project {name} ({e})")
    return False

@dataclass
class Project:
    name: str
    path: str
    options: dict[str, float]
    metadata: dict[str, str]
        
def scan_projects() -> list[Project]:
    """scans all saved projects"""
    
    log.info(f"Scanning projects root /{SAVES_PATH}...")
    projects: list[Project] = []
    for entry in os.scandir(SAVES_PATH):
        if not entry.is_dir(): continue     #   skip if not a folder
        log.debug(f"Found directory /{entry.path}")
        
        metadata: dict[str, float] = None
        
        log.debug(f"Scanning files...")
        for item in os.scandir(entry.path):
            if not item.is_file(): continue
            log.debug(f"Found file /{item.name}")
            
            #   read and load project files
            match item.name:
                case "metadata.json":
                    content = load_json(item.path)
                    if not content: continue
                    metadata = content
                    
                case "options.json":
                    content = load_json(item.path)
                    if not content: continue
                    options: dict[str, float] = content
                case _: continue
        
        if metadata: 
            log.info(f"'{entry.name}' is a project directory")
            projects.append(Project(entry.name, entry.path, options, metadata))
        else:
            log.warning(f"'{entry.name}' is not a project directory")
    projects.sort(key=lambda x: os.path.getctime(os.path.join(SAVES_PATH, x.name)), reverse=True)
    return projects

def read_project(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    
    log.info(f"Reading project directory /{path}...")
    filepath = os.path.join(path, "grid")
    os.makedirs(filepath, exist_ok=True)
    try:
        u = v = s = w = None
        for item in os.scandir(filepath):
            if not item.is_file(): continue
            log.debug(f"Found file /{item.path}")
            
            match item.name:
                case "u.npy": u = load_npy(item.path)
                case "v.npy": v = load_npy(item.path)
                case "w.npy": w = load_npy(item.path)
                case "s.npy": s = load_npy(item.path)
                case "_": continue
        if u is None: log.warning("Missing u field.")
        if v is None: log.warning("Missing v field.")
        if s is None: log.warning("Missing s field.")
        if w is None: log.warning("Missing w field.")
        return u, v, s, w
        
    except FileNotFoundError as e:
        log.error(f"filepath /{filepath} not found, ({e})")
    return None, None, None, None

def save_project(path: str, u: np.ndarray, v: np.ndarray, s: np.ndarray, w: np.ndarray) -> None:
    
    log.info(f"Saving to project directory /{path}...")
    filepath = os.path.join(path, "grid")
    save_npy(filepath, "u", u)
    save_npy(filepath, "v", v)
    save_npy(filepath, "s", s)
    save_npy(filepath, "w", w)