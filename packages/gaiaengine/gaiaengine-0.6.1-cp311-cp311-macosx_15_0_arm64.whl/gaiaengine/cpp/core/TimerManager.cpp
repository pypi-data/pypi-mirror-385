
#include "TimerManager.h"

#include "Window.h"

Timer::Timer(const py::function& callback, float tickRate, bool loop, bool absolute) :
  _callback(callback),
  _loop(loop),
  _absolute(absolute)
{
  _tickRateMs = (int)(tickRate * 1000);

  if (_tickRateMs < 0)
    throw std::invalid_argument("The timer tick rate cannot be negative");
}

void Timer::triggerCallback() {
  if (!isActive())
    return;

  _callback();

  if (!_loop)
    cancel();
}


void TimerManager::update(int /*msElapsed*/) {
  updateInternal(_stepTimers, _activeTimers, getWindow()->getSimulationTime());
}

void TimerManager::updateVisuals(int /*msElapsed*/, const Camera* /*camera*/) {
  updateInternal(_absoluteStepTimers, _activeAbsoluteTimers, getWindow()->getAbsoluteTime());
}

void TimerManager::updateInternal(std::list<std::shared_ptr<Timer>>& stepTimers, std::multimap<int, std::shared_ptr<Timer>>& activeTimers, int time) {
  for (auto stepTimer = stepTimers.begin(); stepTimer != stepTimers.end();) {
    (*stepTimer)->triggerCallback();

    if ((*stepTimer)->isActive())
      stepTimer++;
    else
      stepTimer = stepTimers.erase(stepTimer);
  }

  for (auto timerCall = activeTimers.begin(); timerCall != activeTimers.end() && timerCall->first < time;)
  {
    std::shared_ptr<Timer> timer = timerCall->second;
    int nbCallsToFire = (time - timerCall->first) / timer->getTickRate() + 1;
    int nextCallTimestamp = timerCall->first + nbCallsToFire * timer->getTickRate();

    timerCall = activeTimers.erase(timerCall);

    for (int i = 0; i < nbCallsToFire; i++) {
      timer->triggerCallback();

      if (!timer->isActive())
        break;
    }

    if (timer->isActive())
      activeTimers.insert(std::pair<int, std::shared_ptr<Timer>>(nextCallTimestamp, timer));
  }
}

std::shared_ptr<Timer> TimerManager::addTimer(std::shared_ptr<Timer> timer) {
  if (!timer->isActive())
    return nullptr;

  if (timer->_absolute) {
    if (timer->getTickRate() == 0)
      _absoluteStepTimers.push_back(timer);
    else
      _activeAbsoluteTimers.insert(std::pair<int, std::shared_ptr<Timer>>(getWindow()->getAbsoluteTime() + timer->getTickRate(), timer));
  }

  else {
    if (timer->getTickRate() == 0)
      _stepTimers.push_back(timer);
    else
      _activeTimers.insert(std::pair<int, std::shared_ptr<Timer>>(getWindow()->getSimulationTime() + timer->getTickRate(), timer));
  }

  return timer;
}

void Timer::pythonBindings(py::module& m) {
  py::class_<Timer, std::shared_ptr<Timer>>(m, "Timer")
    .def(py::init<>())
    .def(py::init<const py::function&, float, bool, bool>())
    .def_readwrite("callback", &Timer::_callback)
    .def_property_readonly("tickRate", &Timer::getTickRate)
    .def_readwrite("loop", &Timer::_loop)
    .def("cancel", &Timer::cancel)
    .def("isActive", &Timer::isActive);
}

void TimerManager::pythonBindings(py::module& m) {
  py::class_<TimerManager, std::shared_ptr<TimerManager>, Component>(m, "TimerManager")
    .def(py::init<std::shared_ptr<Window>>())
    .def("addTimer", py::overload_cast<std::shared_ptr<Timer>>(&TimerManager::addTimer))
    .def("addTimer", py::overload_cast<const py::function&, float, bool>(&TimerManager::addTimer))
    .def("addAbsoluteTimer", &TimerManager::addAbsoluteTimer);
}

