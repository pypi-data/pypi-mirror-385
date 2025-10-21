#pragma once

#include <imgui.h>
#include <imgui_markdown.h>
#include <glm/glm.hpp>
#include "opengl.h"

#include "Color.h"
#include "Component.h"
#include "Manager.h"
#include "UIElement.h"

#include <memory>
#include <string>
#include <vector>

class Texture;


class UIManager : public Component, public Manager<UIElement> {
public:
  UIManager(std::shared_ptr<Window> window);
  ~UIManager();
  UIManager(UIManager const&) = delete;
  void operator=(UIManager const&) = delete;

  void updateVisuals(int msElapsed, const Camera* camera) override;
  void render(const Camera* camera) const override;

  // If the italic and bold variants aren't provided, they will be generated automatically by freetype
  // They are used for markdown text
  void setDefaultFont(const std::string& fontPath, float sizePx, const std::string& italicPath = std::string(), const std::string& boldPath = std::string()) const;
  void setH1Font(const std::string& fontPath, float sizePx, bool showSeparator = true);
  void setH2Font(const std::string& fontPath, float sizePx, bool showSeparator = true);
  void setH3Font(const std::string& fontPath, float sizePx, bool showSeparator = true);

  static void Image(const Texture& texture, const glm::vec2& size, const glm::vec2& uv0 = glm::vec2(0.f), const glm::vec2& uv1 = glm::vec2(1.f), const Color& tint_col = Color(1.f, 1.f, 1.f), const Color& border_col = Color());
  static bool ImageButton(const Texture& texture, const glm::vec2& size, const glm::vec2& uv0 = glm::vec2(0.f), const glm::vec2& uv1 = glm::vec2(1.f), int frame_padding = -1, const Color& bg_col = Color(), const Color& tint_col = Color(1.f, 1.f, 1.f));
  static bool ImageButtonFixedRatio(const Texture& texture, const glm::vec2& size, int frame_padding = -1, const Color& bg_col = Color(), const Color& tint_col = Color(1.f, 1.f, 1.f));

  void Markdown(const std::string& text) const;

  static void pythonBindings(py::module& m);

private:
  static void MarkdownFormatCallback(const ImGui::MarkdownFormatInfo& markdownFormatInfo, bool start);

  static ImGui::MarkdownConfig _markdownConfig;
  static ImFont* _italicFont;
  static ImFont* _boldFont;
};
