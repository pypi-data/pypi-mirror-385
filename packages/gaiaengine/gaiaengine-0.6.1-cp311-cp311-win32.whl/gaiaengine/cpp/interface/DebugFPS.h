#pragma once

#include "InGameText.h"

#include <array>

class DebugFPS : public InGameText {
public:
  DebugFPS(std::shared_ptr<UIManager> uiManager);

  void buildFrame() override;

  static void pythonBindings(py::module& m);

private:
  glm::ivec2 _screenPosition = glm::ivec2(0);
  float _tickRate = 0.2f;

  std::array<float, 4> _accumulatedValues{};
  int _accumulatedTimeMs = 0;
  int _nbAccumulatedValues = 0;

  int _previousElapsedSimTime = 0;
};