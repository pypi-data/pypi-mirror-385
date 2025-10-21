#include "Component.h"

#include "Window.h"

Component::Component(std::shared_ptr<Window> window) : ManagedElement(window) {}

std::shared_ptr<Window> Component::getWindow() const {
  return std::static_pointer_cast<Window>(getManager());
}

void Component::pythonBindings(py::module& m) {
  py::class_<Component, std::shared_ptr<Component>, ManagedElement>(m, "Component");
}
