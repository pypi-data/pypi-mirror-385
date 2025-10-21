import gaiaengine as gaia

from .aoe_unit import AoEUnit
from .aoe_terrain import AoETerrain

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import json
import math
import os

from . import AOE_COMMON_DIR, AOE_INSTALL_DIR, LOCAL_ASSET_DIR, cache_aoe_file


class AoELoader:
    """Loads an age of empires scenario file and parses into data readable by gaia
    Supports caching to a json file to avoid having to parse the scenario for each run
    """

    # Contains the loaded assets, the key being the unit id
    ASSETS = {}

    with open(os.environ["GAIA_SOURCE_PATH"] + "/res/unit_id_to_slp_info.json", 'r') as slp_info_file:
        slp_info = json.load(slp_info_file)
        SLP_IDS = slp_info['unit_id_to_slp_id']
        ANIM_DURATIONS = slp_info['unit_id_to_anim_duration']
        REPLAY_DELAYS = slp_info['unit_id_to_replay_delay']

    def __init__(self, scenario_file, **kwargs):
        try:
            cached_data = open(self.get_scenario_cache_name(scenario_file))
            self.__dict__ = json.load(cached_data)

        except IOError:
            self._load_from_scenario(scenario_file)

        # If loaded_units is empty, all units will be loaded
        self.loaded_units = []
        if 'loaded_units' in kwargs:
            self.loaded_units = kwargs['loaded_units']

        self.excluded_units = []
        if 'excluded_units' in kwargs:
            self.excluded_units = kwargs['excluded_units']

        self.create_unit = AoELoader.create_unit
        if 'create_unit' in kwargs:
            self.create_unit = kwargs['create_unit']

    @staticmethod
    def get_scenario_cache_name(scenario_file):
        return str(scenario_file) + str(".json")

    def _load_from_scenario(self, scenario_file):
        scenario = AoE2DEScenario.from_file(scenario_file)

        self._map_data = [[tile.terrain_id, tile.elevation] for tile in scenario.map_manager.terrain]

        self._unit_data = {}
        for unit in scenario.unit_manager.units[0]:
            # Using strings to have the same behavior than after loading the info from a json file
            self._unit_data.setdefault(str(unit.unit_const), []).append(unit.x)
            self._unit_data.setdefault(str(unit.unit_const), []).append(unit.y)
            self._unit_data.setdefault(str(unit.unit_const), []).append(unit.rotation)

        with open(self.get_scenario_cache_name(scenario_file), 'w') as outfile:
            json.dump({"_map_data": self._map_data, "_unit_data": self._unit_data}, outfile)

    def init_window(self, window):        
        if not hasattr(window, "heightmap") or window.heightmap is None:
            window.heightmap = window.create(AoETerrain, self._map_data)
        else:
            window.heightmap.reset(self._map_data)

        if not isinstance(window.camera, gaia.HeightmapCamera):
            window.camera = gaia.HeightmapCamera(window.heightmap)
            window.event_manager.create(gaia.HeightmapCameraInput, window.camera, window.timer_manager)

        if not hasattr(window, "unit_manager") or window.unit_manager is None:
            window.unit_manager = window.create(gaia.UnitManager, window.heightmap)
            window.unit_manager.baseUnitSizeFactor = 0.01
        else:
            for unit in window.unit_manager.getElements():
                unit.delete()

        for key, unit_info in self._unit_data.items():
            # We need to convert the key to an int because int keys are not supported in json,
            # so the loaded dict will have string keys instead
            intkey = int(key)
            if self.loaded_units and intkey not in self.loaded_units:
                continue

            if self.excluded_units and intkey in self.excluded_units:
                continue

            try:
                asset = self.get_asset_from_unit_id(intkey)
                it = iter(unit_info)
                # It seems like age of empires coordinate are inverted, not using a right-handed coordinate system
                [self.create_unit(window.unit_manager, asset, gaia.Vec2(y, x), rotation) for
                x, y, rotation
                in zip(it, it, it)]
            except KeyError:
                print("No SLP info for unit id: " + key)
            except IOError as e:
                print(str(e) + " - unit id: " + key)

    @staticmethod
    def create_unit(unit_manager, asset, position, rotation):
        class_to_create = AoEUnit if isinstance(asset, gaia.AnimatedUnitAsset) else gaia.Unit
        return unit_manager.create(class_to_create, asset, position)

    @staticmethod
    def get_slp_path(slp_id):
        paths_to_try = [AOE_COMMON_DIR + "drs/graphics/" + str(slp_id) + ".slp",
                        AOE_COMMON_DIR + "drs/gamedata_x2/" + str(slp_id) + ".slp",
                        LOCAL_ASSET_DIR + str(slp_id) + ".slp"]
        
        for path in paths_to_try:
            if os.path.exists(path):
                return path
        
        raise IOError("No SLP file found for SLP ID: " + str(slp_id) + ", AOE install folder: " + AOE_INSTALL_DIR)

    @staticmethod
    def is_moving_unit(unit_id):
        return AoELoader.ANIM_DURATIONS[str(unit_id)][0] > 0.0

    @staticmethod
    def get_asset_from_unit_id(unit_id):
        if unit_id in AoELoader.ASSETS:
            return AoELoader.ASSETS[unit_id]

        str_unit_id = str(unit_id)
        slp_file_list = [AoELoader.get_slp_path(slp_id) if slp_id != 0 else "" for slp_id in AoELoader.SLP_IDS[str_unit_id]]

        if AoELoader.is_moving_unit(unit_id):
            asset = gaia.AnimatedUnitAsset(slp_file_list, AoELoader.ANIM_DURATIONS[str_unit_id], AoELoader.REPLAY_DELAYS[str_unit_id])
        else:
            asset = gaia.UnitAsset(slp_file_list)

        for slp_file in slp_file_list:
            cache_aoe_file(slp_file)

        asset.unitID = unit_id
        AoELoader.ASSETS[unit_id] = asset
        return asset
