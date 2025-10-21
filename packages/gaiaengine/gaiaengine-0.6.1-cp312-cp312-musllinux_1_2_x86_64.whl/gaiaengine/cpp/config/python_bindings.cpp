#include <glm/glm.hpp>
#include <glm/gtx/string_cast.hpp>
#include <glm/gtx/vector_angle.hpp>

// Base types
#include "Manager.h"

// Core
#include "Camera.h"
#include "Component.h"
#include "Context.h"
#include "Window.h"

// Event handling
#include "EventListener.h"
#include "EventManager.h"

// Heightmap
#include "Heightmap.h"
#include "HeightmapCamera.h"
#include "HeightmapSelector.h"

// Units
#include "Unit.h"
#include "UnitAsset.h"
#include "AnimatedUnitAsset.h"
#include "UnitManager.h"
#include "UnitSelector.h"

// Interface
#include "UIElement.h"
#include "Plot.h"
#include "InGameText.h"
#include "DebugFPS.h"
#include "UIManager.h"

// OpenGL
#include "Texture.h"

// Utilities
#include "Chrono.h"
#include "Clock.h"
#include "Color.h"
#include "Delegate.h"
#include "TimerManager.h"

#include <pybind11/operators.h>

// Exposing GLM vector types

template <int DIM, typename T>
py::class_<glm::vec<DIM, T>> addGLMFunctions(py::class_<glm::vec<DIM, T>> pyClass) {
  pyClass
    .def(py::self == py::self)
    .def(py::self + py::self)
    .def(py::self += py::self)
    .def(py::self - py::self)
    .def(py::self -= py::self)
    .def(py::self * py::self)
    .def(py::self *= T())
    .def(T() * py::self)
    .def(py::self * T())
    .def(py::self / T());

  return pyClass;
}

template <typename T>
py::class_<glm::vec<2, T>> exposeGLMVec2(py::module& m, const std::string& pythonName) {
  return addGLMFunctions<2, T>(
    py::class_<glm::vec<2, T>>(m, pythonName.c_str())
      .def(py::init<T>())
      .def(py::init<T, T>())
      .def_property("x", [](const glm::vec<2, T>& v) { return v.x; }, [](glm::vec<2, T>& v, T val) { v.x = val; })
      .def_property("y", [](const glm::vec<2, T>& v) { return v.y; }, [](glm::vec<2, T>& v, T val) { v.y = val; })
      .def("__repr__", [](const glm::vec<2, T>& v) { return glm::to_string(v); })
  );
}

template <typename T>
py::class_<glm::vec<3, T>> exposeGLMVec3(py::module& m, const std::string& pythonName) {
  return addGLMFunctions<3, T>(
    py::class_<glm::vec<3, T>>(m, pythonName.c_str())
      .def(py::init<T>())
      .def(py::init<T, glm::vec<2, T>>())
      .def(py::init<glm::vec<2, T>, T>())
      .def(py::init<T, T, T>())
      .def_property("x", [](const glm::vec<3, T>& v) { return v.x; }, [](glm::vec<3, T>& v, T val) { v.x = val; })
      .def_property("y", [](const glm::vec<3, T>& v) { return v.y; }, [](glm::vec<3, T>& v, T val) { v.y = val; })
      .def_property("z", [](const glm::vec<3, T>& v) { return v.z; }, [](glm::vec<3, T>& v, T val) { v.z = val; })
      .def("__repr__", [](const glm::vec<3, T>& v) { return glm::to_string(v); } )
  );
}

template <typename T>
py::class_<glm::vec<4, T>> exposeGLMVec4(py::module& m, const std::string& pythonName) {
  return addGLMFunctions<4, T>(
    py::class_<glm::vec<4, T>>(m, pythonName.c_str())
      .def(py::init<T>())
      .def(py::init<T, T, glm::vec<2, T>>())
      .def(py::init<T, glm::vec<2, T>, T>())
      .def(py::init<glm::vec<2, T>, T, T>())
      .def(py::init<glm::vec<2, T>, glm::vec<2, T>>())
      .def(py::init<T, glm::vec<3, T>>())
      .def(py::init<glm::vec<3, T>, T>())
      .def(py::init<T, T, T, T>())
      .def_property("x", [](const glm::vec<4, T>& v) { return v.x; }, [](glm::vec<4, T>& v, T val) { v.x = val; })
      .def_property("y", [](const glm::vec<4, T>& v) { return v.y; }, [](glm::vec<4, T>& v, T val) { v.y = val; })
      .def_property("z", [](const glm::vec<4, T>& v) { return v.z; }, [](glm::vec<4, T>& v, T val) { v.z = val; })
      .def_property("w", [](const glm::vec<4, T>& v) { return v.w; }, [](glm::vec<4, T>& v, T val) { v.w = val; })
      .def("__repr__", [](const glm::vec<4, T>& v) { return glm::to_string(v); })
  );
}

PYBIND11_MODULE(gaiaengine, m) {
  // Exposing glm vectors
  //exposeGLMVec2<bool>(m, "bVec2"); // Bools need to be exposed in a different way, with different operators
  //exposeGLMVec3<bool>(m, "bVec3");
  //exposeGLMVec4<bool>(m, "bVec4");
  m.def("length", [](const glm::vec2& v) { return glm::length(v); });
  m.def("length", [](const glm::vec3& v) { return glm::length(v); });
  m.def("length", [](const glm::vec4& v) { return glm::length(v); });
  m.def("length2", [](const glm::vec2& v) { return glm::length2(v); });
  m.def("length2", [](const glm::vec3& v) { return glm::length2(v); });
  m.def("length2", [](const glm::vec4& v) { return glm::length2(v); });
  m.def("distance", [](const glm::vec2& u, const glm::vec2& v) { return glm::distance(u, v); });
  m.def("distance", [](const glm::vec3& u, const glm::vec3& v) { return glm::distance(u, v); });
  m.def("distance", [](const glm::vec4& u, const glm::vec4& v) { return glm::distance(u, v); });
  m.def("distance2", [](const glm::vec2& u, const glm::vec2& v) { return glm::distance2(u, v); });
  m.def("distance2", [](const glm::vec3& u, const glm::vec3& v) { return glm::distance2(u, v); });
  m.def("distance2", [](const glm::vec4& u, const glm::vec4& v) { return glm::distance2(u, v); });
  m.def("dot", [](const glm::vec2& u, const glm::vec2& v) { return glm::dot(u, v); });
  m.def("dot", [](const glm::vec3& u, const glm::vec3& v) { return glm::dot(u, v); });
  m.def("dot", [](const glm::vec4& u, const glm::vec4& v) { return glm::dot(u, v); });
  m.def("orientedAngle", [](const glm::vec2& u, const glm::vec2& v) { return glm::orientedAngle(u, v); });
  m.def("orientedAngle", [](const glm::vec3& u, const glm::vec3& v, const glm::vec3& w) { return glm::orientedAngle(u, v, w); });

  exposeGLMVec2<float>(m, "Vec2").def("normalize", &glm::normalize<2, float, glm::packed_highp>);
  exposeGLMVec3<float>(m, "Vec3").def("normalize", &glm::normalize<3, float, glm::packed_highp>);
  exposeGLMVec4<float>(m, "Vec4").def("normalize", &glm::normalize<4, float, glm::packed_highp>);
  exposeGLMVec2<int>(m, "iVec2");
  exposeGLMVec3<int>(m, "iVec3");
  exposeGLMVec4<int>(m, "iVec4");
  exposeGLMVec2<unsigned int>(m, "uVec2");
  exposeGLMVec3<unsigned int>(m, "uVec3");
  exposeGLMVec4<unsigned int>(m, "uVec4");

  // Base types
  ManagedElement::pythonBindings(m);
  ManagerBase::pythonBindings(m);
  TestManagedElement::pythonBindings(m);
  TestManager::pythonBindings(m);

  // Core
  Camera::pythonBindings(m);
  Component::pythonBindings(m);
  Context::pythonBindings(m);
  Window::pythonBindings(m);

  // Utilities
  Clock::pythonBindings(m);
  Chrono::pythonBindings(m);
  Color::pythonBindings(m);
  Delegate::pythonBindings(m);
  Timer::pythonBindings(m);
  TimerManager::pythonBindings(m);

  // Event handling
  EventListener::pythonBindings(m);
  EventManager::pythonBindings(m);

  // Heightmap
  Heightmap::pythonBindings(m);
  HeightmapCamera::pythonBindings(m);
  HeightmapSelector::pythonBindings(m);

  // Unit
  Unit::pythonBindings(m);
  UnitAsset::pythonBindings(m);
  AnimatedUnitAsset::pythonBindings(m);
  UnitManager::pythonBindings(m);
  UnitSelector::pythonBindings(m);

  // Interface
  UIElement::pythonBindings(m);
  Plot::pythonBindings(m);
  InGameText::pythonBindings(m);
  DebugFPS::pythonBindings(m);
  UIManager::pythonBindings(m);

  // OpenGL
  Texture::pythonBindings(m);
}
