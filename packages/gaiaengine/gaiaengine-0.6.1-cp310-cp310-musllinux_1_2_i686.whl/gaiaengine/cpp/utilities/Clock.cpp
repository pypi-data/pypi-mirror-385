#include "Clock.h"

#include <SDL.h>

int Clock::getAbsoluteTime() {
  return SDL_GetTicks();
}

Clock::Clock() :
  _msInitialTime(getTime())
{}

int Clock::getElapsedTime() const {
  return getTime() - _msInitialTime;
}

void Clock::restart() {
  _msInitialTime = getTime();
}

int Clock::getTime() const {
  return Clock::getAbsoluteTime();
}

void Clock::pythonBindings(py::module& m) {
  py::class_<Clock, std::shared_ptr<Clock>>(m, "Clock")
    .def_static("getAbsoluteTime", &Clock::getAbsoluteTime);
}
