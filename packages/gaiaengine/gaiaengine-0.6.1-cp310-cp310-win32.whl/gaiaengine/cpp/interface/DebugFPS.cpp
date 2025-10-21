#include "DebugFPS.h"

#include <imgui.h>

#include "UIManager.h"
#include "utils.h"
#include "Window.h"

#include <string>
#include <sstream>

DebugFPS::DebugFPS(std::shared_ptr<UIManager> uiManager) :
  InGameText(uiManager),
  _screenPosition(getWindow()->getWindowSize().x - 40, getWindow()->getWindowSize().y / 3)
{}

void DebugFPS::buildFrame() {
  std::shared_ptr<Window> window = getWindow();

  _accumulatedValues[0] += 1000.f / window->getFrameTime();
  _accumulatedValues[1] += 1000.f / window->getFrameTime() * (window->getSimulationTime() - _previousElapsedSimTime) / window->getMsSimulationStep();
  _accumulatedValues[2] += 100.f * (float)window->getMsFrameTimeRender() / (float)window->getFrameTime();
  _accumulatedValues[3] += window->getSimulationSpeedFactor();

  _accumulatedTimeMs += window->getFrameTime();
  _nbAccumulatedValues++;

  _previousElapsedSimTime = window->getSimulationTime();

  if (_accumulatedTimeMs >= (int)(_tickRate * 1000)) {
    clearText();

    for (int i = 0; i < _accumulatedValues.size(); i++) {
      std::string nextString = std::string(i, '\n') + ut::to_string_with_precision(_accumulatedValues[i] / (float)_nbAccumulatedValues, 2);
      pushText(TextElement{nextString, _screenPosition - glm::ivec2(ImGui::CalcTextSize(nextString.c_str()).x, 0.f)});

      _accumulatedValues[i] = 0.f;
    }

    std::stringstream labelsStream;
    labelsStream << "FPS" << std::endl
      << "Sim FPS" << std::endl
      << "Render time %" << std::endl
      << "Sim speed factor" << std::endl;

    pushText(TextElement{labelsStream.str(), _screenPosition - glm::ivec2(ImGui::CalcTextSize(labelsStream.str().c_str()).x + 80.f * window->getDPIZoom() , 0)});

    _accumulatedTimeMs = 0;
    _nbAccumulatedValues = 0;
  }

  InGameText::buildFrame();
}

void DebugFPS::pythonBindings(py::module& m) {
  py::class_<DebugFPS, std::shared_ptr<DebugFPS>, InGameText>(m, "DebugFPS")
    .def(py::init<std::shared_ptr<UIManager>>())
    .def_readwrite("screenPosition", &DebugFPS::_screenPosition)
    .def_readwrite("tickRate", &DebugFPS::_tickRate);
}