#include "EventManager.h"

#include <imgui.h>
#include <imgui_internal.h>
#include <imgui_impl_sdl.h>

#include "Clock.h"
#include "utils.h"
#include "EventListener.h"
#include "Window.h"

const Uint32 EventManager::EVENT_CLICK = SDL_RegisterEvents(1);
const Uint32 EventManager::EVENT_LONG_CLICK_BEGIN = SDL_RegisterEvents(1);
const Uint32 EventManager::EVENT_LONG_CLICK_MOTION = SDL_RegisterEvents(1);
const Uint32 EventManager::EVENT_LONG_CLICK_END = SDL_RegisterEvents(1);
const Uint32 EventManager::EVENT_DRAG_BEGIN = SDL_RegisterEvents(1);
const Uint32 EventManager::EVENT_DRAG_MOTION = SDL_RegisterEvents(1);
const Uint32 EventManager::EVENT_DRAG_END = SDL_RegisterEvents(1);

bool EventManager::isCloseEnoughToBeginClickToDefineClick(int x, int y) const {
  if (x == -INT_MAX && y == -INT_MAX)
    return false;

  glm::vec2 beginDrag(_beginDrag);
  glm::vec2 posFloat(x, y);

  return glm::length(beginDrag - posFloat) < _maxDistanceForClick * getWindow()->getDPIZoom();
}

void EventManager::modifyTypeAndSendEvent(const SDL_Event& event, Uint32 newType) const {
  SDL_Event newEvent = event;
  newEvent.type = newType;
  SDL_PushEvent(&newEvent);
}

void EventManager::updateVisuals(int /*msElapsed*/, const Camera*) {  
  SDL_Event event;
  while (SDL_PollEvent(&event)) {
    processEvent(getWindow(), event);
  }

  if (!isDuringLongClick() && SDL_GetMouseState(nullptr, nullptr) & SDL_BUTTON_LMASK) {
    if (_clickBegin.getElapsedTime() > _longClickTimeout && !isDraggingCursor()) {
      SDL_Event newEvent;
      SDL_zero(newEvent);
      newEvent.type = EVENT_LONG_CLICK_BEGIN;
      SDL_GetMouseState(&newEvent.button.x, &newEvent.button.y);
      SDL_PushEvent(&newEvent);
      _duringLongClick = true;
    }
  }
}

bool EventManager::processEvent(std::shared_ptr<Window> window, SDL_Event& event) {
  // We want to see if an event listener consumed a base event to prevent firing an associated custom event
  // e.g. if MOUSEBUTTONDOWN was consumed, we don't want to fire EVENT_CLICK
  bool wasConsumed = false;

  if (ImGui::GetCurrentContext()) // Only process interface events if it has been initialized
    wasConsumed = processEventForInterface(event);

  if (!wasConsumed) {
    // The last registered event listener should be processed first since it will be drawn on top
    std::vector<std::shared_ptr<EventListener>> managedElements = getElements();
    for (auto eventListener = managedElements.rbegin(); eventListener != managedElements.rend(); ++eventListener) {
      if ((*eventListener)->isActive() && (*eventListener)->handleEvent(window, event)) {
        wasConsumed = true;
        break;
      }
    }
  }

  fireCustomEvents(event, wasConsumed);

  return wasConsumed;
}

bool EventManager::processEventForInterface(SDL_Event& event) {
  ImGui_ImplSDL2_ProcessEvent(&event);

  switch (event.type) {
  case SDL_MOUSEBUTTONDOWN:
  case SDL_MOUSEBUTTONUP:
  case SDL_MOUSEWHEEL:
  case SDL_MOUSEMOTION:
    return ImGui::GetIO().WantCaptureMouse;
  case SDL_KEYDOWN:
  case SDL_KEYUP:
    // Escape closes popups on top of the stack
    if (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE) {
      ImGuiWindow* topMostPopup = ImGui::GetTopMostPopupModal();
      if (topMostPopup != nullptr)
        topMostPopup->Active = false;
    }
    return ImGui::GetIO().WantCaptureKeyboard;
  }

  if (event.type == EventManager::EVENT_CLICK ||
    event.type == EventManager::EVENT_LONG_CLICK_BEGIN ||
    event.type == EventManager::EVENT_LONG_CLICK_MOTION ||
    event.type == EventManager::EVENT_DRAG_BEGIN ||
    event.type == EventManager::EVENT_DRAG_MOTION)
    return ImGui::GetIO().WantCaptureMouse;

  return false;
}

void EventManager::fireCustomEvents(SDL_Event & event, bool wasConsumed) {
  switch (event.type) {
    case SDL_MOUSEBUTTONDOWN:
      if (wasConsumed)
        break;

      _beginDrag.x = event.button.x;
      _beginDrag.y = event.button.y;

      _clickBegin.restart();
      break;

    case SDL_MOUSEMOTION:
      if (wasConsumed)
        break;

      if (SDL_GetMouseState(nullptr, nullptr) & SDL_BUTTON_LMASK) {
        if (isDuringLongClick())
          modifyTypeAndSendEvent(event, EVENT_LONG_CLICK_MOTION);

        else if (!isCloseEnoughToBeginClickToDefineClick(event.motion.x, event.motion.y) && !isDraggingCursor() && _beginDrag != glm::ivec2(-INT_MAX)) {
          SDL_Event newEvent = event;
          newEvent.type = EVENT_DRAG_BEGIN;
          newEvent.motion.xrel = event.motion.x - _beginDrag.x;
          newEvent.motion.yrel = event.motion.y - _beginDrag.y;
          SDL_PushEvent(&newEvent);
          _duringDrag = true;
        }

        else if (isDraggingCursor())
          modifyTypeAndSendEvent(event, EVENT_DRAG_MOTION);
      }
      break;

    case SDL_MOUSEBUTTONUP: {
      if (event.button.button == SDL_BUTTON_LEFT) {
        if (!wasConsumed) {
          if (isCloseEnoughToBeginClickToDefineClick(event.button.x, event.button.y)) {
            if (_clickBegin.getElapsedTime() < _longClickTimeout)
              modifyTypeAndSendEvent(event, EVENT_CLICK);
          }

          if (isDuringLongClick())
            modifyTypeAndSendEvent(event, EVENT_LONG_CLICK_END);

          else if (isDraggingCursor())
            modifyTypeAndSendEvent(event, EVENT_DRAG_END);
        }

        _duringLongClick = false;
        _duringDrag = false;
        _beginDrag = glm::ivec2(-INT_MAX);
      }
      break;
    }
  }

  //userEventLog(event);
}

void EventManager::userEventLog(const SDL_Event& event) const {
  if (event.type == SDL_MOUSEBUTTONDOWN)
    SDL_Log("Button down: (%d,%d)", event.button.x, event.button.y);
  if (event.type == SDL_MOUSEBUTTONUP)
    SDL_Log("Button up: (%d,%d)", event.button.x, event.button.y);
  if (event.type == EVENT_CLICK)
    SDL_Log("Click: (%d,%d)", event.button.x, event.button.y);
  if (event.type == EVENT_LONG_CLICK_BEGIN)
    SDL_Log("Long click begin: (%d,%d)", event.button.x, event.button.y);
  if (event.type == EVENT_LONG_CLICK_MOTION)
    SDL_Log("Long click motion: (%d,%d)", event.motion.x, event.motion.y);
  if (event.type == EVENT_LONG_CLICK_END)
    SDL_Log("Long click end: (%d,%d)", event.button.x, event.button.y);
  if (event.type == EVENT_DRAG_BEGIN)
    SDL_Log("Drag begin: (%d,%d)", event.motion.x, event.motion.y);
  if (event.type == EVENT_DRAG_MOTION)
    SDL_Log("Drag motion: (%d,%d)", event.motion.x, event.motion.y);
  if (event.type == EVENT_DRAG_END)
    SDL_Log("Drag end: (%d,%d)", event.button.x, event.button.y);
}

class PyEventManager : public EventManager {
public:
  using EventManager::EventManager;

  virtual bool processEvent(std::shared_ptr<Window> window, SDL_Event& event) {
    PYBIND11_OVERRIDE_NAME(bool, EventManager, "_processEvent", processEvent, window, event);
  }
};

void EventManager::pythonBindings(py::module& m) {
  py::class_<EventManager, std::shared_ptr<EventManager>, Component, ManagerBase, PyEventManager>(m, "EventManager_", py::multiple_inheritance())
    .def(py::init<std::shared_ptr<Window>>())
    .def("_processEvent", &EventManager::processEvent)
    .def_readwrite("maxDistanceForClick", &EventManager::_maxDistanceForClick)
    .def_readwrite("longClickTimeout", &EventManager::_longClickTimeout);

  m.attr("EVENT_CLICK") = EventManager::EVENT_CLICK;
  m.attr("EVENT_LONG_CLICK_BEGIN") = EventManager::EVENT_LONG_CLICK_BEGIN;
  m.attr("EVENT_LONG_CLICK_MOTION") = EventManager::EVENT_LONG_CLICK_MOTION;
  m.attr("EVENT_LONG_CLICK_END") = EventManager::EVENT_LONG_CLICK_END;
  m.attr("EVENT_DRAG_BEGIN") = EventManager::EVENT_DRAG_BEGIN;
  m.attr("EVENT_DRAG_MOTION") = EventManager::EVENT_DRAG_MOTION;
  m.attr("EVENT_DRAG_END") = EventManager::EVENT_DRAG_END;
}
