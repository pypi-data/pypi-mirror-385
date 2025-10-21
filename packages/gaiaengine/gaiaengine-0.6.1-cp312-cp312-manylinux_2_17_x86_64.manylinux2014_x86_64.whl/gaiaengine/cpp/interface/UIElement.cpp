#include "UIElement.h"

#include "UIManager.h"
#include "Window.h"

int UIElement::nextID = 0;

UIElement::UIElement(std::shared_ptr<UIManager> uiManager):
  ManagedElement(uiManager),
  _ID(std::to_string(nextID))
{
  nextID++;
}

class PyUIElement : public UIElement {
public:
  using UIElement::UIElement;

  void buildFrame() override {
    PYBIND11_OVERRIDE(void, UIElement, buildFrame, );
  }
};

void UIElement::pythonBindings(py::module& m) {
  py::class_<UIElement, std::shared_ptr<UIElement>, ManagedElement, PyUIElement>(m, "UIElement")
    .def(py::init<std::shared_ptr<UIManager>>())
    .def_property_readonly("id", &UIElement::getID)
    .def_property("enabled", &UIElement::isEnabled, &UIElement::setEnabled)
    .def_property("position", &UIElement::getPosition, &UIElement::setPosition)
    .def_property("pivot", &UIElement::getPivot, &UIElement::setPivot);
}
