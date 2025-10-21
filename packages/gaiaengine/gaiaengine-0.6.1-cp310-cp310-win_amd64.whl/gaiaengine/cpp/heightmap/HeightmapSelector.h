#pragma once

#include <glm/glm.hpp>

#include "Component.h"
#include "Heightmap.h"

#include <memory>
#include <vector>

class HeightmapSelector : public Component {
public:
  HeightmapSelector(std::shared_ptr<Window> window, std::shared_ptr<Heightmap> selectedHeightmap);
  HeightmapSelector(std::shared_ptr<Window> window, std::shared_ptr<Heightmap> selectedHeightmap, const glm::ivec2& size);

  void updateVisuals(int msElapsed, const Camera* camera) override;
  void render(const Camera* camera) const override;

  glm::vec2 getPointedPos() { return glm::vec2(_renderedSelector.getOriginOffset()) + glm::vec2(getSize() / 2); }
  void setPointedPos(const glm::vec2& pointedPos);

  const std::vector<float>& updateSelectorHeights();
  void setHeights(std::vector<float> heights);

  void setPointedColor(const Color& color);
  Color getColor() const { return _renderedSelector.getColor(glm::ivec2(0)); }
  void setColor(const Color& color) { _renderedSelector.setColors(std::vector<Color>(getNbVertices().x * getNbVertices().y, color)); }

  inline glm::ivec2 getSize() const { return glm::ivec2(getNbVertices().x - 1, getNbVertices().y - 1); }
  void setSize(const glm::ivec2& size);

  static void pythonBindings(py::module& m);

private:
  inline glm::ivec2 getNbVertices() const { return _renderedSelector.getNbVertices(); }
  inline glm::vec2 getOriginOffset() const { return _renderedSelector.getOriginOffset(); }

  Heightmap _renderedSelector;
  std::shared_ptr<Heightmap> _selectedHeightmap;

  bool _autoUpdatePointedPos = true;
};
