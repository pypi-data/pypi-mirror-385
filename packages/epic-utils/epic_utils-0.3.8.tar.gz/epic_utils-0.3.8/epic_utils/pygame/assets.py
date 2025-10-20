from ..fileSys import File
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg


def load_assets(directory: str):
    if not File.existsDir(directory):
        return {}
    
    result = {}
    
    directory = directory if File.isAbsPath(directory) else File.toAbsPath(directory)
    dirs = [directory,]
    
    while len(dirs) > 0:
        current = dirs.pop(0)
        files = File.listDir(current)
        for file in files:
            path = os.path.join(current, file)
            if File.existsDir(path):
                dirs.append(path)
            else:
                local_path = path.lstrip(directory)
                temp = local_path.split("\\")
                temp.pop(-1)
                current_sub_dir = result
                
                for key in temp:
                    if key not in list(current_sub_dir.keys()):
                        current_sub_dir[key] = {}
                    current_sub_dir = current_sub_dir[key]
                current_sub_dir[file] = pg.image.load(path)            
    return result