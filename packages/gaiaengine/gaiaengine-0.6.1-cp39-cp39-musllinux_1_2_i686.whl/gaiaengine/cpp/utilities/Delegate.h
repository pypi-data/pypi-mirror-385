#pragma once

#include <vector>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Delegate {
public:
  Delegate() = default;

  void bind(const py::function& callback);
  void unbind(const py::function& callback);
  void unbindAll();

  // Disable binding anything to this delegate
  void deactivate();

  void broadcast(py::args args = py::args());

  static void pythonBindings(py::module& m);
private:
  bool _isActive = true;
  std::vector<py::function> _callbacks;
};
