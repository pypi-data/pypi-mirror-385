import os
from pathlib import Path
import platform
import shutil
import vdf
import winreg

import __main__
LOCAL_ASSET_DIR = os.path.join(os.path.dirname(__main__.__file__), ".aoe_assets/")

NOT_FOUND_STRING = "AOE_INSTALL_NOT_FOUND"
AOE_INSTALL_DIR = NOT_FOUND_STRING
AOE_COMMON_DIR = NOT_FOUND_STRING

def get_steam_path_windows():
    steam_key_x64 = r"SOFTWARE\Wow6432Node\Valve\Steam"
    steam_key_x86 = r"SOFTWARE\Valve\Steam"

    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        try:
            key = winreg.OpenKey(registry, steam_key_x64)
        except FileNotFoundError:
            key = winreg.OpenKey(registry, steam_key_x86)

        steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
        return steam_path
    except Exception as e:
        print(f"Error reading registry: {e}")
        return None
    
def get_steam_path_linux():
    possible_paths = [
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/.local/share/Steam"),
        os.path.expanduser("~/Steam")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path

def get_steam_libraries(steam_path):
    config_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if not os.path.exists(config_path):
        return [os.path.join(steam_path, "steamapps")]

    libraries = []
    try:
        with open(config_path, encoding='utf-8') as f:
            data = vdf.load(f)
            folders = data['libraryfolders']

            for key in folders:
                folder_data = folders[key]
                if isinstance(folder_data, dict) and 'path' in folder_data:
                    path = folder_data['path']
                else:
                    path = folder_data  # for older Steam versions

                libraries.append(os.path.join(path, "steamapps"))

    except Exception as e:
        print(f"Error parsing libraryfolders.vdf: {e}")
        return [os.path.join(steam_path, "steamapps")]

    return libraries

def find_aoe_install_dir(library_folder):
    try:
        for filename in os.listdir(str(Path(library_folder))):
            if filename.endswith('.acf'):
                with open(str(Path(library_folder).joinpath(filename)), 'r') as file:
                    steamapp = vdf.load(file)
                    # The Steam AppID for Age of Empires II HD (2013)
                    if steamapp['AppState']['appid'] == "221380":
                        return str(Path(library_folder).joinpath("common").joinpath(steamapp['AppState']['installdir']))
                
    except (FileNotFoundError, KeyError, IsADirectoryError, ValueError):
        pass
    
    return ""


# Find the Age of Empires installation and add it to AOE_INSTALL_DIR
try:
    if platform.system() == 'Windows':
        steam_path = get_steam_path_windows()
    elif platform.system() == 'Linux':
        steam_path = get_steam_path_linux()
    else:
        raise ValueError("Platform not supported to find an Age of Empires install")
    
    steam_libraries = get_steam_libraries(steam_path)

    for steam_library in steam_libraries:
        aoe_install_dir = find_aoe_install_dir(steam_library)

        if aoe_install_dir:
            AOE_INSTALL_DIR = aoe_install_dir
            AOE_COMMON_DIR = AOE_INSTALL_DIR + "/resources/_common/"
            break

    if AOE_INSTALL_DIR == NOT_FOUND_STRING:
        raise RuntimeError("No Age of Empires install found")

except Exception as e:
    print(f"Unable to set the Age of Empires install folder: {e}")

def cache_aoe_file(filename):
    if gaia.is_packaged_simulation():
        return 
    
    if not os.path.exists(LOCAL_ASSET_DIR):
        os.makedirs(LOCAL_ASSET_DIR)

    try:
        if not os.path.exists(LOCAL_ASSET_DIR + Path(filename).name):
            shutil.copy2(filename, LOCAL_ASSET_DIR)
    except:
        pass

from .aoe_loader import *
from .aoe_unit import *
from .aoe_terrain import *