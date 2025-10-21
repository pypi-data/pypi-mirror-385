import gaiaengine as gaia
import sdl2


class UnitSelectorInput(gaia.EventListener):
    def __init__(self, event_manager, selector):
        super().__init__(event_manager)
        self.selector = selector
        
        self.heightmap_camera = None
        self.click_to_lock_on = False  # Also disables double click selection
        self.lock_on_timer = None
        self.lock_on_camera_radius = 12.0
        self.lerp_time_lock_on = 0.2

        self.rotation_speed = 0.1

    def start_lock_on(self, unit, heightmap_camera):
        heightmap_camera.lockedOnUnit = unit
        heightmap_camera.lerpTimeMs = (int)(self.lerp_time_lock_on * 1000)
        heightmap_camera.radius = self.lock_on_camera_radius
        self.heightmap_camera = heightmap_camera
        if self.lock_on_timer is None:
            self.lock_on_timer = self.window.timer_manager.addAbsoluteTimer(self.update_lock_on, 0.0, True)

    def stop_lock_on(self):
        if self.lock_on_timer is not None:
            self.lock_on_timer.cancel()
            self.lock_on_timer = None
            self.heightmap_camera.lockedOnUnit = None
            self.heightmap_camera = None

    def update_lock_on(self):
        locked_on_unit = self.heightmap_camera.lockedOnUnit

        if locked_on_unit is None:
            self.stop_lock_on()
            return
    
        if locked_on_unit not in self.selector.selection or not locked_on_unit.canBeSelected:
            self.selector.removeFromSelection(locked_on_unit)
            self.stop_lock_on()
            return
        
        # Dezooming unlocks the camera
        if self.heightmap_camera.radius != self.lock_on_camera_radius:
            self.stop_lock_on()
            return

    def handleEvent(self, window, event):
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.scancode == sdl2.SDL_SCANCODE_SPACE:
                window.camera.lerpTimeMs = (int)(self.lerp_time_lock_on * 1000)
                self.selector.goBackToSelection(window.camera)
                return True

            elif event.key.keysym.scancode == sdl2.SDL_SCANCODE_DELETE:
                self.selector.deleteOneInSelection()
                return True

        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            # Save the location of where dragging was started, but don't show the selection rectangle yet (see EVENT_DRAG_BEGIN)
            self.selector.selectionRectangle = gaia.iVec4(event.button.x, event.button.y, 0, 0)

            if event.button.button == sdl2.SDL_BUTTON_RIGHT:
                if not self.selector.isSelectionEmpty():
                    self.selector.moveSelection(window.camera.screenToWorldPos(gaia.iVec2(event.button.x, event.button.y)))
                    return True
                
        elif event.type == sdl2.SDL_MOUSEBUTTONUP:
            if event.button.button == sdl2.SDL_BUTTON_LEFT and event.button.clicks == 2 and not self.manager.is_touch_event(event):
                clicked_unit = self.selector.getSelectableUnit(gaia.iVec2(event.button.x, event.button.y), self.manager.get_selection_leniency(event))
                # Only select similar units on double click if the first click already selected the unit
                # and if we're not locking on to that unit
                if clicked_unit is not None and clicked_unit in self.selector.selection and not self.click_to_lock_on:
                    selection_rectangle = gaia.iVec4(0, 0, window.windowSize)
                    add_to_selection = sdl2.SDL_GetKeyboardState(None)[sdl2.SDL_SCANCODE_LSHIFT]
                    double_click_filter = lambda unit : unit.type == clicked_unit.type and unit.asset == clicked_unit.asset
                    self.selector.select(selection_rectangle, add_to_selection, double_click_filter)
                    return True

        elif event.type == gaia.EVENT_CLICK:
            should_consume = False

            selectable_unit = self.selector.getSelectableUnit(gaia.iVec2(event.button.x, event.button.y), self.manager.get_selection_leniency(event))

            if not self.selector.isSelectionEmpty():
                if selectable_unit is None or not sdl2.SDL_GetKeyboardState(None)[sdl2.SDL_SCANCODE_LSHIFT]:
                    self.selector.clearSelection()
                should_consume = True

            if selectable_unit is not None:
                self.selector.addToSelection(selectable_unit)
                should_consume = True
                if self.manager.is_touch_event(event) or (self.click_to_lock_on and not sdl2.SDL_GetKeyboardState(None)[sdl2.SDL_SCANCODE_LSHIFT]):
                    self.start_lock_on(selectable_unit, window.camera)
            
            return should_consume
        
        # Rotation around locked-on unit
        if self.lock_on_timer is not None and window.camera == self.heightmap_camera:
            if event.type == gaia.EVENT_DRAG_MOTION:
                screen_rect = window.camera.lockedOnUnit.screenRect
                # The direction of rotation depends on which quarter of the screen the cursor is
                if event.motion.x > screen_rect.x + screen_rect.z / 2:
                    window.camera.theta += event.motion.yrel * self.rotation_speed
                else:
                    window.camera.theta -= event.motion.yrel * self.rotation_speed

                if event.motion.y < screen_rect.y + screen_rect.w / 2:
                    window.camera.theta += event.motion.xrel * self.rotation_speed
                else:
                    window.camera.theta -= event.motion.xrel * self.rotation_speed

        # Handle the selection rectangle except for touch input
        elif not self.manager.is_touch_event(event):
            if event.type == gaia.EVENT_DRAG_BEGIN:
                # Only start displaying the selection rectangle when it cannot be considered a click anymore
                self.selector.displaySelectionRectangle = True
                return True

            elif event.type == gaia.EVENT_DRAG_MOTION:
                selection_rectangle = self.selector.selectionRectangle
                selection_rectangle.z = event.motion.x - selection_rectangle.x
                selection_rectangle.w = event.motion.y - selection_rectangle.y
                self.selector.selectionRectangle = selection_rectangle
                return True

            elif event.type == gaia.EVENT_DRAG_END:
                add_to_selection = sdl2.SDL_GetKeyboardState(None)[sdl2.SDL_SCANCODE_LSHIFT]
                self.selector.select(self.selector.selectionRectangle, add_to_selection)
                self.selector.displaySelectionRectangle = False
                return True

        return False