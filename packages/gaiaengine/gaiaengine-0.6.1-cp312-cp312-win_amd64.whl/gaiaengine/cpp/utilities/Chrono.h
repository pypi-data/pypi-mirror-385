#pragma once

#include "Clock.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Chrono {
public:
  Chrono(int msTime);

  inline void reset(int msTime) {
    _msTime = msTime;
    _clock.restart();
  }

  inline int getTotalTime() const { return _msTime; }

  inline int getRemainingTime() const {
    return std::max(0, _msTime - _clock.getElapsedTime());
  }

  inline int getElapsedTime() const {
    return _clock.getElapsedTime();
  }

  inline float getPercentageElapsed() const {
    return std::min((float)_clock.getElapsedTime() / _msTime, 1.f);
  }

  inline bool isStillRunning() const {
    return getRemainingTime() != 0;
  }

  static void pythonBindings(py::module& m);
private:
  int _msTime = 0;

  Clock _clock;
};
