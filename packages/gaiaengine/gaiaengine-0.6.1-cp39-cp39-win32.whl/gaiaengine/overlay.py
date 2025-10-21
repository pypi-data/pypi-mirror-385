import gaiaengine as gaia
from gaiaengine import imgui

from enum import Enum


class GuiAnchor(Enum):
    NONE, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT = range(5)


class Overlay(gaia.UIElement):
    def __init__(self, manager, anchor_point, text=""):
        super().__init__(manager)
        self.corner = anchor_point.value - 1  # Hack to convert from the enum to imgui's way of handling corners
        self.text = text
        self.padding_top = 10.0
        self.padding_bottom = 10.0
        self.padding_left = 10.0
        self.padding_right = 10.0

    def getText(self):
        return self.text
    
    def buildFrame(self):
        # See ShowExampleAppWindowTitles() in imgui_demo.cpp
        io = imgui.get_io()
        window_pos_x = io.display_size.x - self.padding_right if self.corner & 1 else self.padding_left
        window_pos_y = io.display_size.y - self.padding_bottom if self.corner & 2 else self.padding_top
        window_pos_pivot_x = 1.0 if self.corner & 1 else 0.0
        window_pos_pivot_y = 1.0 if self.corner & 2 else 0.0
        if self.corner != -1:
            imgui.set_next_window_position(window_pos_x, window_pos_y, imgui.ALWAYS, window_pos_pivot_x, window_pos_pivot_y)
        
        imgui.set_next_window_bg_alpha(0.3)
        if imgui.begin("##" + self.id, None, (imgui.WINDOW_NO_MOVE if self.corner != -1 else 0) | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_FOCUS_ON_APPEARING | imgui.WINDOW_NO_NAV):
            imgui.text_unformatted(self.getText())
            if imgui.begin_popup_context_window():
                if imgui.menu_item("Custom", None, self.corner == -1)[0]:
                    self.corner = -1
                if imgui.menu_item("Top-left", None, self.corner == 0)[0]:
                    self.corner = 0
                if imgui.menu_item("Top-right", None, self.corner == 1)[0]:
                    self.corner = 1
                if imgui.menu_item("Bottom-left", None, self.corner == 2)[0]:
                    self.corner = 2
                if imgui.menu_item("Bottom-right", None, self.corner == 3)[0]:
                    self.corner = 3
                imgui.end_popup()
        imgui.end()