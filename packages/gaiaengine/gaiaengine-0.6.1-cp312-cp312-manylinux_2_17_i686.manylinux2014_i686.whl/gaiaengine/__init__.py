import datetime
import os
from pathlib import Path
import platform
import sys
import __main__

os.environ["PYSDL2_DLL_PATH"] = os.path.dirname(__file__)
os.environ["GAIA_SOURCE_PATH"] = os.path.dirname(__file__)

def is_packaged_simulation():
    try:
        sys._MEIPASS  # Only set on simulations packaged by PyInstaller (see tools/create_standalone_app.py)
        return True
    except:
        return False

def get_or_spawn_save_folder(simulation_name, force_system_save=False):
    # Use the local directory for non-packaged simulations
    if not force_system_save and not is_packaged_simulation():
        return Path(__main__.__file__).parent
    
    # Otherwise use a standard cache folder
    if platform.system() == 'Windows':
        gaia_path = Path(os.getenv('APPDATA')).joinpath('Gaia')
    else:
        gaia_path = Path(os.path.expanduser('~')).joinpath('.gaia')
    
    gaia_path.mkdir(exist_ok=True)
    sim_path = gaia_path.joinpath(simulation_name)
    sim_path.mkdir(exist_ok=True)

    return sim_path

# Check if we have a file specifying an expiry date
EXPIRY_DATE_FILENAME = 'expiry_date.txt' 
try:
    with open(str(Path(__main__.__file__).parent.joinpath(EXPIRY_DATE_FILENAME)), "r") as file:
        date_str = file.read().strip()
        expiry_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        current_date = datetime.datetime.now()

        if current_date >= expiry_date:
            raise RuntimeError("This version is expired")
except FileNotFoundError:
    pass

from .gaiaengine import *
from .event_manager import *
from .event_listener import *
from .heightmap_camera_input import *
from .unit_selector_input import *
from .media_bar import *
from .overlay import *
from .ui_manager import *
from .window import *