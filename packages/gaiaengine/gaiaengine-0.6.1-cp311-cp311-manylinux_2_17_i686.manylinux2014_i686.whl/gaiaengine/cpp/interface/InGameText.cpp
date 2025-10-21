#include "InGameText.h"

#include <imgui.h>

#include "UIManager.h"

void InGameText::buildFrame() {
  ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);

  for (int i = 0; i < _texts.size(); i++) {
    ImGui::SetNextWindowPos(_texts[i].screenPosition, ImGuiCond_Always, _texts[i].pivot);
    ImGui::SetNextWindowBgAlpha(0.f);
    if (ImGui::Begin(("##" + getID() + "." + std::to_string(i)).c_str(), nullptr, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoFocusOnAppearing | ImGuiWindowFlags_NoInputs))
      ImGui::TextUnformatted(_texts[i].text.c_str());
    ImGui::End();
  }

  ImGui::PopStyleVar();
}

void InGameText::pythonBindings(py::module& m) {
  py::class_<InGameText, std::shared_ptr<InGameText>, UIElement>(m, "InGameText")
    .def(py::init<std::shared_ptr<UIManager>>());
}
