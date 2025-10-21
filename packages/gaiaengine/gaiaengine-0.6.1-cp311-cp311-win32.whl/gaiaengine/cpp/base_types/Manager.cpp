#include "Manager.h"

#include "Component.h"
#include "Window.h"

void ManagedElement::deleteElement() {
  if (!isElementDeleted()) {
    getManager()->deleteElement(_indexInManager, _isPendingAdd);
    _isDeleted = true;
    _objectToKeepAlive = py::object();
  }
}

std::shared_ptr<Window> ManagedElement::getWindow() const {
  std::shared_ptr<Component> component = std::dynamic_pointer_cast<Component>(getManager());
  
  if (!component)
    throw std::runtime_error("This element is not managed by a Component, can't get the associated Window");

  return component->getWindow();
}

void ManagedElement::pythonBindings(py::module& m) {
  py::class_<ManagedElement, std::shared_ptr<ManagedElement>>(m, "ManagedElement")
    .def("delete", &ManagedElement::deleteElement)
    .def("isDeleted", &ManagedElement::isElementDeleted)
    .def_property_readonly("window", &ManagedElement::getWindow)
    .def_property_readonly("manager", &ManagedElement::getManager);
}

#include <pybind11/functional.h>
#include <pybind11/stl.h>

void ManagerBase::pythonBindings(py::module& m) {
  py::class_<ManagerBase, std::shared_ptr<ManagerBase>>(m, "Manager")
    .def("create", &ManagerBase::createManagedElement)
    .def("createAt", &ManagerBase::createManagedElementAt)
    .def("getElements", &ManagerBase::getManagedElementsByFilter, py::arg("filter") = py::none());
}

void TestManagedElement::pythonBindings(py::module& m) {
  py::class_<TestManagedElement, std::shared_ptr<TestManagedElement>, ManagedElement>(m, "TestManagedElement")
    .def(py::init<std::shared_ptr<ManagerBase>>());
}

void TestManager::pythonBindings(py::module& m) {
  py::class_<TestManager, std::shared_ptr<TestManager>, ManagerBase>(m, "TestManager")
    .def(py::init<>());
}