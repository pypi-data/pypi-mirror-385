#include "UIManager.h"

#include <imgui_internal.h>
#include <misc/freetype/imgui_freetype.h>
#include <implot.h>
#include <imgui_impl_sdl.h>
#include <imgui_impl_opengl3.h>

#include "Context.h"
#include "EventManager.h"
#include "Program.h"
#include "Texture.h"
#include "UIElement.h"
#include "utils.h"
#include "Window.h"

#include <cmath>

ImGui::MarkdownConfig UIManager::_markdownConfig;
ImFont* UIManager::_italicFont = nullptr;
ImFont* UIManager::_boldFont = nullptr;

UIManager::UIManager(std::shared_ptr<Window> window) :
  Component(window)
{
  // Setup Dear ImGui context
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImPlot::CreateContext();

  // Setup Platform/Renderer bindings
  ImGui_ImplSDL2_InitForOpenGL(window->getSDLWindow(), Context::getGLContext());
  ImGui_ImplOpenGL3_Init(Program::getGLSLVersion().c_str());

  _markdownConfig.formatCallback = &UIManager::MarkdownFormatCallback;
}

UIManager::~UIManager() {
  ImGui_ImplOpenGL3_Shutdown();
  ImGui_ImplSDL2_Shutdown();
  ImPlot::DestroyContext();
  ImGui::DestroyContext();
}

void UIManager::updateVisuals(int /*msElapsed*/, const Camera*) {
  ImGui_ImplOpenGL3_NewFrame();
  ImGui_ImplSDL2_NewFrame(getWindow()->getSDLWindow());
  ImGui::NewFrame();

  for (auto& uiElement : getElements()) {
    if (uiElement->isEnabled()) {
      if (uiElement->getPosition() != glm::vec2(-FLT_MAX))
        ImGui::SetNextWindowPos(uiElement->getPosition(), ImGuiCond_Always, uiElement->getPivot());

      uiElement->buildFrame();
    }
  }

  ImGui::Render();
}

void UIManager::render(const Camera*) const {
  if (ImGui::GetDrawData()) {
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
  }
}

void UIManager::setDefaultFont(const std::string& fontPath, float sizePx, const std::string& italicPath, const std::string& boldPath) const {
  float DPIZoom = getWindow()->getDPIZoom();
  ImGui::GetStyle().ScaleAllSizes(std::floor(DPIZoom * sizePx / 13.f));
  ImGui::GetIO().Fonts->AddFontFromFileTTF(fontPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f));
  
  // Load italic and bold variants
  ImFontConfig fontConfig;
  fontConfig.FontBuilderFlags |= ImGuiFreeTypeBuilderFlags_Oblique;
  if (italicPath.empty())
    _italicFont = ImGui::GetIO().Fonts->AddFontFromFileTTF(fontPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f), &fontConfig);
  else
    _italicFont = ImGui::GetIO().Fonts->AddFontFromFileTTF(italicPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f));

  fontConfig.FontBuilderFlags &= ~ImGuiFreeTypeBuilderFlags_Oblique;
  fontConfig.FontBuilderFlags |= ImGuiFreeTypeBuilderFlags_Bold;
  if (boldPath.empty())
    _boldFont = ImGui::GetIO().Fonts->AddFontFromFileTTF(fontPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f), &fontConfig);
  else
    _boldFont = ImGui::GetIO().Fonts->AddFontFromFileTTF(boldPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f));
}

void UIManager::setH1Font(const std::string& fontPath, float sizePx, bool showSeparator /*= true*/) {
  float DPIZoom = getWindow()->getDPIZoom();
  _markdownConfig.headingFormats[0].font = ImGui::GetIO().Fonts->AddFontFromFileTTF(fontPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f));
  _markdownConfig.headingFormats[0].separator = showSeparator;
}

void UIManager::setH2Font(const std::string& fontPath, float sizePx, bool showSeparator /*= true*/) {
  float DPIZoom = getWindow()->getDPIZoom();
  _markdownConfig.headingFormats[1].font = ImGui::GetIO().Fonts->AddFontFromFileTTF(fontPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f));
  _markdownConfig.headingFormats[1].separator = showSeparator;
}

void UIManager::setH3Font(const std::string& fontPath, float sizePx, bool showSeparator /*= true*/) {
  float DPIZoom = getWindow()->getDPIZoom();
  _markdownConfig.headingFormats[2].font = ImGui::GetIO().Fonts->AddFontFromFileTTF(fontPath.c_str(), std::floor(DPIZoom * sizePx + 0.1f));
  _markdownConfig.headingFormats[2].separator = showSeparator;
}

void UIManager::Image(const Texture& texture, const glm::vec2& size, const glm::vec2& uv0 /*= glm::vec2(0.f)*/, const glm::vec2& uv1 /*= glm::vec2(1.f)*/, const Color& tint_col /*= Color(1.f, 1.f, 1.f)*/, const Color& border_col /*= Color()*/) {
  ImGui::Image((void*)(intptr_t)texture.getObjectID(), size, uv0, uv1, tint_col.getRGBAFloat(), border_col.getRGBAFloat());
}

bool UIManager::ImageButton(const Texture& texture, const glm::vec2& size, const glm::vec2& uv0 /*= glm::vec2(0.f)*/, const glm::vec2& uv1 /*= glm::vec2(1.f)*/, int frame_padding /*= -1*/, const Color& bg_col /*= Color()*/, const Color& tint_col /*= Color(1.f, 1.f, 1.f)*/) {
  return ImGui::ImageButton((void*)(intptr_t)texture.getObjectID(), size, uv0, uv1, frame_padding, bg_col.getRGBAFloat(), tint_col.getRGBAFloat());
}

bool UIManager::ImageButtonFixedRatio(const Texture& texture, const glm::vec2& size, int frame_padding /*= -1*/, const Color& bg_col /*= Color()*/, const Color& tint_col /*= Color(1.f, 1.f, 1.f)*/) {
  // Code taken from ImGui::ImageButton Begin
  ImGuiContext& g = *GImGui;
  ImGuiWindow* window = g.CurrentWindow;
  if (window->SkipItems)
    return false;

  // Default to using texture ID as ID. User can still push string/integer prefixes.
  ImGui::PushID((void*)(intptr_t)texture.getObjectID());
  const ImGuiID id = window->GetID("#image");
  ImGui::PopID();

  glm::vec2 padding = (frame_padding >= 0) ? glm::vec2((float)frame_padding) : glm::vec2(g.Style.FramePadding);
  // Code taken from ImGui::ImageButton End

  const glm::vec2 textureSize = texture.getSize();
  float textureRatio = textureSize.x / textureSize.y;
  float targetRatio = size.x / size.y;
  glm::vec2 paddingToMaintainRatio = (textureRatio > targetRatio ? 
    glm::vec2(0.f, size.y - size.x / textureRatio) :
    glm::vec2(size.x - size.y * textureRatio, 0.f));

  return ImGui::ImageButtonEx(id, (void*)(intptr_t)texture.getObjectID(), size - paddingToMaintainRatio, glm::vec2(0.f), glm::vec2(1.f), padding + paddingToMaintainRatio / 2.f, bg_col.getRGBAFloat(), tint_col.getRGBAFloat());
}

void UIManager::Markdown(const std::string& text) const {
  ImGui::Markdown(text.c_str(), text.length(), _markdownConfig);
}

void UIManager::MarkdownFormatCallback(const ImGui::MarkdownFormatInfo& markdownFormatInfo, bool start) {
  switch (markdownFormatInfo.type) {

  // Handle bold and italics manually
  case ImGui::MarkdownFormatType::EMPHASIS:
  {
    if (markdownFormatInfo.level == 1) {
      // normal emphasis
      if (start)
        ImGui::PushFont(_italicFont);
      
      else
        ImGui::PopFont();
    }
    else {
      // strong emphasis
      if (start)
        ImGui::PushFont(_boldFont);

      else
        ImGui::PopFont();
    }
    break;
  }
  case ImGui::MarkdownFormatType::HEADING:
  {
    ImGui::MarkdownHeadingFormat fmt;
    if (markdownFormatInfo.level > ImGui::MarkdownConfig::NUMHEADINGS)
      fmt = markdownFormatInfo.config->headingFormats[ImGui::MarkdownConfig::NUMHEADINGS - 1];
    else
      fmt = markdownFormatInfo.config->headingFormats[markdownFormatInfo.level - 1];

    if (start) {
      ImGui::NewLine();
      ImGui::PushFont(fmt.font);
    }
    else {
      if (fmt.separator)
        ImGui::Separator();

      ImGui::PopFont();
      ImGui::NewLine();
    }
    break;
  }
  default:
    ImGui::defaultMarkdownFormatCallback(markdownFormatInfo, start);
  }
}


void UIManager::pythonBindings(py::module& m) {
  py::class_<UIManager, std::shared_ptr<UIManager>, Component, ManagerBase>(m, "UIManager_", py::multiple_inheritance())
    .def(py::init<std::shared_ptr<Window>>())
    .def("setDefaultFont", &UIManager::setDefaultFont, py::arg("fontPath"), py::arg("sizePx"), py::arg("italicPath") = std::string(), py::arg("boldPath") = std::string())
    .def("markdown", &UIManager::Markdown)
    .def("setH1Font", &UIManager::setH1Font, py::arg("fontPath"), py::arg("sizePx"), py::arg("showSeparator") = true)
    .def("setH2Font", &UIManager::setH2Font, py::arg("fontPath"), py::arg("sizePx"), py::arg("showSeparator") = true)
    .def("setH3Font", &UIManager::setH3Font, py::arg("fontPath"), py::arg("sizePx"), py::arg("showSeparator") = true);

  m.def("image", &UIManager::Image, py::arg("texture"), py::arg("size"), py::arg("uv0") = glm::vec2(0.f), py::arg("uv1") = glm::vec2(1.f), py::arg("tint_col") = Color(1.f, 1.f, 1.f), py::arg("border_col") = Color());
  m.def("image_button", &UIManager::ImageButton, py::arg("texture"), py::arg("size"), py::arg("uv0") = glm::vec2(0.f), py::arg("uv1") = glm::vec2(1.f), py::arg("frame_padding") = -1, py::arg("bg_col") = Color(), py::arg("tint_col") = Color(1.f, 1.f, 1.f));
  m.def("image_button_fixed_ratio", &UIManager::ImageButtonFixedRatio, py::arg("texture"), py::arg("size"), py::arg("frame_padding") = -1, py::arg("bg_col") = Color(), py::arg("tint_col") = Color(1.f, 1.f, 1.f));
}