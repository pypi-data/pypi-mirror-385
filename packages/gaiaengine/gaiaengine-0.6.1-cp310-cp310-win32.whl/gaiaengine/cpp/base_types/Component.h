#pragma once

#include "Manager.h"

#include <memory>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Camera;
class Window;

class Component : public ManagedElement {
public:
  Component(std::shared_ptr<Window> window);
  virtual ~Component() = default;

  virtual void update(int /*msElapsed*/) {}
  virtual void updateVisuals(int /*msElapsed*/, const Camera*) {}
  virtual void render(const Camera*) const {}

  std::shared_ptr<Window> getWindow() const override;

  static void pythonBindings(py::module& m);
};
