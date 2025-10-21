#pragma once

#include <SDL.h>
#include <glm/glm.hpp>

#include "Clock.h"
#include "Component.h"
#include "EventListener.h"
#include "Manager.h"

#include <limits>
#include <memory>
#include <unordered_set>
#include <vector>


class EventManager : public Component, public Manager<EventListener> {
public:
  EventManager(std::shared_ptr<Window> window) : Component(window) {}

  void updateVisuals(int /*msElapsed*/, const Camera*) override;

  static const Uint32 EVENT_CLICK;
  static const Uint32 EVENT_LONG_CLICK_BEGIN;
  static const Uint32 EVENT_LONG_CLICK_MOTION;
  static const Uint32 EVENT_LONG_CLICK_END;
  static const Uint32 EVENT_DRAG_BEGIN;
  static const Uint32 EVENT_DRAG_MOTION;
  static const Uint32 EVENT_DRAG_END;

  static void pythonBindings(py::module& m);

protected:
  inline glm::ivec2 getBeginDrag() const {return _beginDrag;}
  inline bool isDuringLongClick() const {return _duringLongClick;}
  inline bool isDraggingCursor() const {return _duringDrag;}

  virtual bool processEvent(std::shared_ptr<Window> window, SDL_Event& event);

private:
  // Returns whether the event should be consumed
  bool processEventForInterface(SDL_Event& event);
  void fireCustomEvents(SDL_Event& event, bool wasConsumed);
  bool isCloseEnoughToBeginClickToDefineClick(int x, int y) const;
  void modifyTypeAndSendEvent(const SDL_Event& event, Uint32 newType) const;

  void userEventLog(const SDL_Event& event) const;

  float _maxDistanceForClick = 20.f;
  int _longClickTimeout = 500;

  bool _duringLongClick = false;
  bool _duringDrag = false;
  glm::ivec2 _beginDrag = glm::ivec2(-INT_MAX);
  Clock _clickBegin;
};
