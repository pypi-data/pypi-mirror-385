#pragma once

#include <glm/glm.hpp>

#include "UIElement.h"

#include <limits>
#include <string>
#include <vector>

struct TextElement {
  std::string text;
  glm::ivec2 screenPosition = glm::ivec2(std::numeric_limits<int>::max());
  glm::vec2 pivot = glm::vec2(0.f);
};


class InGameText : public UIElement {
public:
  InGameText(std::shared_ptr<UIManager> uiManager) : UIElement(uiManager) {}

  void buildFrame() override;

  inline void pushText(const TextElement& textElement) { _texts.push_back(textElement); }

  inline void clearText() { _texts.clear(); }

  static void pythonBindings(py::module& m);
private:
  std::vector<TextElement> _texts;
};