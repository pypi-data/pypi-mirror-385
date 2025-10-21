#include "Delegate.h"

#include "utils.h"

#include <string>

void Delegate::bind(const py::function& callback) {
  if (callback && _isActive)
    _callbacks.push_back(callback);
}

void Delegate::unbind(const py::function& callback) {
  std::erase_if(_callbacks, [callback](const py::function& currentCallback) { return !currentCallback || currentCallback.equal(callback); });
}

void Delegate::unbindAll() {
  _callbacks.clear();
}

void Delegate::deactivate() {
  unbindAll();
  _isActive = false;
}

void Delegate::broadcast(py::args args) {
  for (int i = 0; i < _callbacks.size(); i++) {
    try {
      _callbacks[i](*args);
    }
    catch (py::error_already_set& exception) {
      if (exception.matches(PyExc_TypeError))
        throw py::type_error(std::string("Invalid broadcast arguments when calling callback ") + ut::pyPrintToString(_callbacks[i]) + exception.what());
      else
        throw exception;
    }
  }
}

void Delegate::pythonBindings(py::module& m) {
  py::class_<Delegate, std::shared_ptr<Delegate>>(m, "Delegate")
    .def(py::init<>())
    .def("bind", &Delegate::bind)
    .def("unbind", &Delegate::unbind)
    .def("unbindAll", &Delegate::unbindAll)
    .def("broadcast", &Delegate::broadcast);
}
