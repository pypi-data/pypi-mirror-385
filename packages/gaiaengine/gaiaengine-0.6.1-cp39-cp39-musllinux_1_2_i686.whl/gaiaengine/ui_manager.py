import gaiaengine as gaia
from gaiaengine import imgui

import os


class UIManager(gaia.UIManager_):
    def __init__(self, window):
        super().__init__(window)

        calibri = os.environ["GAIA_SOURCE_PATH"] + str("/res/fonts/calibri-font-family/")
        self.default_font_path = calibri + "calibri-regular.ttf"
        self.setDefaultFont(self.default_font_path, 16.0, calibri + "calibri-italic.ttf", calibri + "calibri-bold.ttf")
        self.setH1Font(self.default_font_path, 30.0)
        self.setH2Font(self.default_font_path, 24.0)
        self.setH3Font(self.default_font_path, 20.0)