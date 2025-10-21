#include "Chrono.h"

Chrono::Chrono(int msTime /*= 0*/) {
  reset(msTime);
}

void Chrono::pythonBindings(py::module& m) {
  py::class_<Chrono, std::shared_ptr<Chrono>>(m, "Chrono")
    .def(py::init<int>())
    .def("reset", &Chrono::reset)
    .def("getRemainingTime", &Chrono::getRemainingTime)
    .def("getTotalTime", &Chrono::getTotalTime)
    .def("getElapsedTime", &Chrono::getElapsedTime)
    .def("getPercentageElapsed", &Chrono::getPercentageElapsed)
    .def("isStillRunning", &Chrono::isStillRunning);
}
