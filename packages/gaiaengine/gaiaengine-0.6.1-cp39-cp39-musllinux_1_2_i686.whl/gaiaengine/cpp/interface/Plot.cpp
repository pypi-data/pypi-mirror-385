#include "Plot.h"

#include <implot.h>

#include "UIManager.h"

Plot::Plot(std::shared_ptr<UIManager> uiManager, const std::string& title, int flags) :
  UIElement(uiManager),
  _title(title),
  _flags(flags)
{
  ImPlot::GetStyle().Colors[ImPlotCol_FrameBg].w = 0.3f;
  ImPlot::GetStyle().Colors[ImPlotCol_PlotBg].w = 0.5f;
}

void Plot::buildFrame() {
  ImGui::SetNextWindowSize(_size);
  ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, glm::vec2(3.f));
  ImGui::Begin(_title.c_str(), nullptr, _flags);
  ImPlot::PushStyleColor(ImPlotCol_FrameBg, { 0,0,0,0 });
  ImPlot::PushStyleColor(ImPlotCol_PlotBg, { 0,0,0,0 });
  ImPlot::SetNextPlotLimits(0., (double)_axisLimits.x, 0., (double)_axisLimits.y, ImGuiCond_Always);
  if (ImPlot::BeginPlot(_title.c_str(), _xAxisTitle.empty() ? nullptr : _xAxisTitle.c_str(), _yAxisTitle.empty() ? nullptr : _yAxisTitle.c_str(), glm::vec2(-1, -1), ImPlotFlags_NoTitle, ImPlotAxisFlags_NoTickLabels)) {
    for (auto& series : _series) {
      ImPlot::PlotLine(series.name.c_str(), &series.xValues[0], &series.yValues[0], (int)series.xValues.size());
      if (_annotateLastValue)
        ImPlot::AnnotateClamped(series.xValues.back(), series.yValues.back(), glm::vec2(-1, 0), "%s", std::to_string((int)series.yValues.back()).c_str());
    }
    ImPlot::EndPlot();
  }
  ImPlot::PopStyleColor(2);
  ImGui::End();
  ImGui::PopStyleVar();
}

void Plot::addPoint(const std::string& seriesName, float xValue, float yValue) {
  bool alreadyExists = false;
  for (auto& series : _series) {
    if (series.name == seriesName) {
      series.xValues.push_back(xValue);
      series.yValues.push_back(yValue);
      alreadyExists = true;
    }
  }

  if (!alreadyExists)
    _series.push_back({ seriesName, std::vector<float>{xValue}, std::vector<float>{yValue} });

  _axisLimits.x = std::max(_axisLimits.x, xValue);
  _axisLimits.y = std::max(_axisLimits.y, yValue);
}

void Plot::pythonBindings(py::module& m) {
  py::class_<Plot, std::shared_ptr<Plot>, UIElement>(m, "Plot")
    .def(py::init<std::shared_ptr<UIManager>, const std::string&>())
    .def(py::init<std::shared_ptr<UIManager>, const std::string&, int>())
    .def("addPoints", &Plot::addPoint)
    .def("clear", &Plot::clear)
    .def_readwrite("title", &Plot::_title)
    .def_readwrite("flags", &Plot::_flags)
    .def_readwrite("size", &Plot::_size)
    .def_readwrite("xAxisTitle", &Plot::_xAxisTitle)
    .def_readwrite("yAxisTitle", &Plot::_yAxisTitle)
    .def_readwrite("annotateLastValue", &Plot::_annotateLastValue);
}
