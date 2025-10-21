import gaiaengine as gaia
import sdl2


class EventManager(gaia.EventManager_):
    def __init__(self, window):
        super().__init__(window)

        # Whether the mouse should behave the same as touch
        self.simulate_touch = False

        # Use the last motion event to detect whether the mouse is hidden by drag motions
        self.last_motion_was_touch = False

        self.last_touch_id = 0

    def _processEvent(self, window, gaia_event):
        event = sdl2.SDL_Event.from_buffer_copy(gaia_event)

        if event.type == sdl2.SDL_MOUSEMOTION:
            self.last_motion_was_touch = event.motion.which == sdl2.SDL_TOUCH_MOUSEID
         
        elif event.type == sdl2.SDL_FINGERDOWN:
            self.last_touch_id = event.tfinger.touchId

        was_consumed = super()._processEvent(window, gaia_event)

        if event.type == sdl2.SDL_QUIT:
            window.close()
            was_consumed = True

        elif event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE and not was_consumed:
            window.close()
            was_consumed = True

        elif event.type == sdl2.SDL_WINDOWEVENT:
            if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                window.setWindowSize(gaia.iVec2(event.window.data1, event.window.data2))
    
        return was_consumed

    def is_touch_event(self, event):
        return event.motion.which == sdl2.SDL_TOUCH_MOUSEID or self.simulate_touch
    
    def get_selection_leniency(self, event):
        if self.is_touch_event(event):
            return 30.0 * self.window.dpiZoom
        
        return 0.0

