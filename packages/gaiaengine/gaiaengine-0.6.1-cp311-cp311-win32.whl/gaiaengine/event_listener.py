import gaiaengine as gaia
import sdl2


class EventListener(gaia.EventListener_):
    # To be overridden
    def handleEvent(self, window, event):
        pass

    def handleEvent_(self, window, event):
        event = sdl2.SDL_Event.from_buffer_copy(event)

        return self.handleEvent(window, event)
