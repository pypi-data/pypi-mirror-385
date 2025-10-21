#pragma once

#include <glm/glm.hpp>

#include "Manager.h"

#include <string>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class UIManager;
class Window;


class UIElement : public ManagedElement {
public:
  UIElement(std::shared_ptr<UIManager> uiManager);

  virtual void buildFrame() {}

  inline std::string getID() const { return _ID; }

  inline bool isEnabled() const { return _enabled; }
  inline void setEnabled(bool val) { _enabled = val; }

  inline glm::vec2 getPosition() const { return _position; }
  inline void setPosition(glm::vec2 val) { _position = val; }

  inline glm::vec2 getPivot() const { return _pivot; }
  inline void setPivot(glm::vec2 val) { _pivot = val; }

  static void pythonBindings(py::module& m);
private:
  static int nextID;
  std::string _ID;
  bool _enabled = true;
  glm::vec2 _position = glm::vec2(-FLT_MAX);
  glm::vec2 _pivot = glm::vec2(0.f);
};