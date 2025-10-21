#pragma once

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Clock {
public:
  Clock();

  // Time elapsed since the beginning of the program execution
  static int getAbsoluteTime();

  int getElapsedTime() const;
  void restart();

  static void pythonBindings(py::module& m);
private:
  int getTime() const;

  int _msInitialTime = -1;
};
