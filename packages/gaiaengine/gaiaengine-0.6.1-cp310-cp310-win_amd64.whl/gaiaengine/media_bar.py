import gaiaengine as gaia
from gaiaengine import imgui

import os

ui_texture_path = os.environ["GAIA_SOURCE_PATH"] + "/res/media_bar/"


class MediaBar(gaia.UIElement):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Only hide restart button by default
        self.hidden_buttons = [True, False, False, False, False]

        self.restart_texture = gaia.Texture(ui_texture_path + "restart.png")
        self.pause_texture = gaia.Texture(ui_texture_path + "pause.png")
        self.play_texture = gaia.Texture(ui_texture_path + "play.png")
        self.fast_forward_texture = gaia.Texture(ui_texture_path + "fast_forward.png")
        self.fast_forward_triple_texture = gaia.Texture(ui_texture_path + "fast_forward_triple.png")

        self.button_size = gaia.Vec2(35, 15)
        self.additional_tint = gaia.Color(0.9, 0.9, 0.9, 0.9)
        self.fast_speed = 8.0

        self.on_button_pressed = gaia.Delegate()

        self.position = gaia.Vec2(self.window.windowSize.x / 2, 0)
        self.pivot = gaia.Vec2(0.5, 0.0)

    def buildFrame(self):
        imgui.begin("MediaBar", None, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_FOCUS_ON_APPEARING | imgui.WINDOW_NO_NAV)

        if not self.hidden_buttons[0]:
            if gaia.image_button_fixed_ratio(self.restart_texture, self.button_size, tint_col=self.additional_tint):
                self.on_button_pressed.broadcast(0)

            if imgui.is_item_hovered():
                imgui.set_tooltip("Restart")

            imgui.same_line()
            
        if not self.hidden_buttons[1]:
            if gaia.image_button_fixed_ratio(self.pause_texture, self.button_size, tint_col=self.additional_tint):
                self.window.paused = True
                self.on_button_pressed.broadcast(1)

        if not self.hidden_buttons[2]:
            imgui.same_line()
            if gaia.image_button_fixed_ratio(self.play_texture, self.button_size, tint_col=self.additional_tint):
                self.window.paused = False
                self.window.simulationSpeedFactor = 1.0
                self.on_button_pressed.broadcast(2)

        if not self.hidden_buttons[3]:
            imgui.same_line()
            if gaia.image_button_fixed_ratio(self.fast_forward_texture, self.button_size, tint_col=self.additional_tint):
                self.window.paused = False
                self.window.simulationSpeedFactor = self.fast_speed
                self.on_button_pressed.broadcast(3)

        if not self.hidden_buttons[4]:
            imgui.same_line()
            if gaia.image_button_fixed_ratio(self.fast_forward_triple_texture, self.button_size, tint_col=self.additional_tint):
                self.window.paused = False
                self.window.simulationSpeedFactor = 1000000
                self.on_button_pressed.broadcast(4)

        imgui.end()
