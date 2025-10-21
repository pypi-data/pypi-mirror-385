#pragma once

#include <glm/glm.hpp>
#include <imgui.h>

#include "UIElement.h"

#include <string>
#include <vector>


struct Series {
  std::string name;
  std::vector<float> xValues;
  std::vector<float> yValues;
};


class Plot : public UIElement {
public:
  Plot(std::shared_ptr<UIManager> uiManager, const std::string& title) : Plot(uiManager, title, 0) {}
  Plot(std::shared_ptr<UIManager> uiManager, const std::string& title, int flags);

  void buildFrame() override;

  void addPoint(const std::string& seriesName, float xValue, float yValue);

  inline void clear() { _series.clear(); _axisLimits = glm::vec2(0.f); }

  static void pythonBindings(py::module& m);
private:
  std::vector<Series> _series;
  glm::vec2 _axisLimits = glm::vec2(0.f);

  std::string _title;
  int _flags = 0;
  glm::vec2 _size = glm::vec2(350, 250);
  std::string _xAxisTitle;
  std::string _yAxisTitle;
  bool _annotateLastValue = false;
};