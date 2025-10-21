import gaiaengine as gaia
from gaiaengine import imgui
import sdl2


class HeightmapCameraInput(gaia.EventListener):
    def __init__(self, event_manager, camera, timer_manager):
        super().__init__(event_manager)
        self.camera = camera
        self.timer_manager = timer_manager

        self.handle_tick_events_timer()
        self.onSetActive.bind(self.handle_tick_events_timer)

        self.translation_speed = 1.0
        self.rotation_speed = 60.0
        self.scroll_zoom_speed = 4.0
        self.finger_zoom_speed = 5.0
 
        self.min_radius = 12.0
        self.max_radius = 120.0

    def handle_tick_events_timer(self):
        if self.active:
            self.tick_events_timer = self.timer_manager.addAbsoluteTimer(self.tick_events, 0.0, True)
        else:
            self.tick_events_timer.cancel()

    def get_real_translation_value(self, ms_elapsed):
        return self.translation_speed * ms_elapsed * self.camera.radius / 1000.0
    
    def set_radius(self, new_radius):
        self.camera.radius = min(max(new_radius, self.min_radius), self.max_radius)

    def handleEvent(self, window, event):        
        if event.type == sdl2.SDL_MOUSEWHEEL:
            self.set_radius(self.camera.radius - event.wheel.y * self.scroll_zoom_speed)
            
        elif event.type == gaia.EVENT_DRAG_MOTION:
            if sdl2.SDL_GetNumTouchFingers(self.manager.last_touch_id) < 2:
                translation_value = - self.translation_speed * self.camera.radius / 1000.0
                self.camera.translateInCameraCoordinates(event.motion.xrel * translation_value, event.motion.yrel * translation_value)

        elif event.type == sdl2.SDL_MULTIGESTURE:
            self.set_radius(self.camera.radius - event.mgesture.dDist * self.finger_zoom_speed * self.camera.radius)
            self.camera.theta += event.mgesture.dTheta * self.rotation_speed

        return False

    def tick_events(self):
        ms_elapsed = self.window.frameTime
        real_translation_value = self.get_real_translation_value(ms_elapsed)

        # Mouse moving the camera while on the edges
        if (sdl2.SDL_GetWindowGrab(self.window.getSDLWindow()) or sdl2.SDL_GetWindowFlags(self.window.getSDLWindow()) & sdl2.SDL_WINDOW_FULLSCREEN)\
            and not self.manager.last_motion_was_touch:
            mouse_pos = self.window.mousePos

            if mouse_pos.x == 0:
                self.camera.translateInCameraCoordinates(-real_translation_value, 0.0)

            if mouse_pos.y == 0:
                self.camera.translateInCameraCoordinates(0.0, -real_translation_value)

            if mouse_pos.x == self.window.windowSize.x - 1:
                self.camera.translateInCameraCoordinates(real_translation_value, 0.0)

            if mouse_pos.y == self.window.windowSize.y - 1:
                self.camera.translateInCameraCoordinates(0.0, real_translation_value)

        # Keys moving the camera
        if not imgui.get_io().want_capture_keyboard:
            keyboard_state = sdl2.SDL_GetKeyboardState(None)
            if keyboard_state[sdl2.SDL_SCANCODE_UP] or keyboard_state[sdl2.SDL_SCANCODE_W]:
                self.camera.translateInCameraCoordinates(0.0, -real_translation_value)

            if keyboard_state[sdl2.SDL_SCANCODE_DOWN] or keyboard_state[sdl2.SDL_SCANCODE_S]:
                self.camera.translateInCameraCoordinates(0.0, real_translation_value)

            theta = self.camera.theta
            if keyboard_state[sdl2.SDL_SCANCODE_RIGHT] or keyboard_state[sdl2.SDL_SCANCODE_D]:
                self.camera.translateInCameraCoordinates(real_translation_value, 0.0)

            if keyboard_state[sdl2.SDL_SCANCODE_LEFT] or keyboard_state[sdl2.SDL_SCANCODE_A]:
                self.camera.translateInCameraCoordinates(-real_translation_value, 0.0)

            if keyboard_state[sdl2.SDL_SCANCODE_LEFT] or keyboard_state[sdl2.SDL_SCANCODE_Q]:
                theta -= self.rotation_speed * ms_elapsed / 1000.0

            if keyboard_state[sdl2.SDL_SCANCODE_LEFT] or keyboard_state[sdl2.SDL_SCANCODE_E]:
                theta += self.rotation_speed * ms_elapsed / 1000.0

            self.camera.theta = theta
