import gaiaengine as gaia
import sdl2

import ctypes


class Window(gaia.Window_):
    def __init__(self, *args):
        super().__init__(*args)
        self.event_manager = self.create(gaia.EventManager)
        self.timer_manager = self.create(gaia.TimerManager)

    def getSDLWindow(self):
        return ctypes.cast(super().getSDLWindow(), ctypes.POINTER(sdl2.SDL_Window))

    @property
    def mousePos(self):
        x, y = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        return gaia.iVec2(x.value, y.value)

    @mousePos.setter
    def mousePos(self, value):
        sdl2.SDL_WarpMouseInWindow(self.getSDLWindow(), value.x, value.y)

