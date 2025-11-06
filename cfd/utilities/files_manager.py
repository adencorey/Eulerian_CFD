import os
import json
import logging
import shutil

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
        log.error(f"Cannot write to file, please enable permision to write files ({e})")
    except Exception as e:
        log.critical(f"An error has occured when creating {filepath} ({e})")
    return False
        

def load_json(filepath) -> dict:
    
    try:
        with open(filepath, "r") as file:
            log.debug(f"Successfully loaded /{filepath}")
            return json.load(file)
    except ValueError as e:
        log.error(f"Cannot read from {filepath}, json may be corrupted ({e})")
    except PermissionError as e:
        log.error(f"File cannot be read, please enable permission to read files ({e})")
    except Exception as e:
        log.critical(f"An error has occured when loading {filepath} ({e})")
    return False


def edit_json(filepath, content:dict) -> True | False:
    
    try:
        with open(filepath, "w") as file:
            json.dump(content, file, indent=4)
            log.info(f"Successfully edited {filepath}")
            return True
    except PermissionError as e:
        log.error(f"Cannot write to file, please enable permision to write files ({e})")
    except Exception as e:
        log.critical(f"An error has occured when creating {filepath} ({e})")
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
    if create_dir(name, gravity): return
    counter = 1
    while True:
        if not create_dir(f"{name} ({counter})", gravity):
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
        if project["name"] == new_name:
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

        
def scan_projects() -> list[dict[str, str|dict[str, str|int]]]:
    """scans all saved projects"""
    
    log.debug(f"Scanning projects root /{SAVES_PATH}...")
    projects: list[dict] = []
    for entry in os.scandir(SAVES_PATH):
        if not entry.is_dir(): continue     #   skip if not a folder
        log.debug(f"Found directory /{entry.path}")
        
        data = {
            "name": entry.name,
            "options": {},
            "metadata": {}
        }
        
        log.debug(f"Scanning files...")
        for item in os.scandir(entry.path):
            if not item.is_file(): continue
            log.debug(f"Found file /{item.path}")
            
            #   read and load project files
            match item.name:
                case "metadata.json":
                    content = load_json(item.path)
                    if not content: continue
                    data["metadata"] = content
                    
                case "options.json": pass
                case _: continue
        
        if data["metadata"]: 
            log.info(f"{entry.name} is a project directory")
            projects.append(data)
        else:
            log.warning(f"{entry.name} is not a project directory")
    projects.sort(key=lambda x: os.path.getctime(os.path.join(SAVES_PATH, x["name"])), reverse=True)
    return projects