#pragma once

#include "Component.h"

#include <chrono>
#include <functional>
#include <list>
#include <map>
#include <memory>
#include <vector>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class TimerManager;

class Timer {
public:
  Timer() = default;
  Timer(const py::function& callback, float tickRate, bool loop, bool absolute);

  inline int getTickRate() const { return _tickRateMs; }

  inline void cancel() { _callback = py::function(); }
  inline bool isActive() const { return (bool)_callback; }

  static void pythonBindings(py::module& m);
private:
  friend class TimerManager;

  void triggerCallback();

  py::function _callback;
  // A tick rate of 0 means that the timer gets called at each update step
  int _tickRateMs = -1;
  bool _loop = false;
  bool _absolute = false;
};

class TimerManager : public Component {
public:
  using Component::Component;

  void update(int msElapsed) override;
  void updateVisuals(int msElapsed, const Camera* camera) override;

  // Regular timers are based on simulation time. They should be used for logic.
  inline std::shared_ptr<Timer> addTimer(const py::function& callback, float tickRate, bool loop) {
    return addTimer(std::make_shared<Timer>(callback, tickRate, loop, false));
  }

  // Absolute timers are based on real world time. They should be used for visuals and input.
  std::shared_ptr<Timer> addAbsoluteTimer(const py::function& callback, float tickRate, bool loop) {
    return addTimer(std::make_shared<Timer>(callback, tickRate, loop, true));
  }

  std::shared_ptr<Timer> addTimer(std::shared_ptr<Timer> timer);

  static void pythonBindings(py::module& m);
private:
  void updateInternal(std::list<std::shared_ptr<Timer>>& stepTimers, std::multimap<int, std::shared_ptr<Timer>>& activeTimers, int time);

  std::multimap<int, std::shared_ptr<Timer>> _activeTimers;
  std::list<std::shared_ptr<Timer>> _stepTimers;

  std::multimap<int, std::shared_ptr<Timer>> _activeAbsoluteTimers;
  std::list<std::shared_ptr<Timer>> _absoluteStepTimers;
};
