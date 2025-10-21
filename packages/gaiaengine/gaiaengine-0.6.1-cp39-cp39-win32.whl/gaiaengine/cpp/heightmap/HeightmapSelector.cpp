#include "HeightmapSelector.h"

#include <imgui.h>
#include <SDL.h>

#include "Camera.h"
#include "Color.h"
#include "EventManager.h"
#include "Window.h"

HeightmapSelector::HeightmapSelector(std::shared_ptr<Window> window, std::shared_ptr<Heightmap> selectedHeightmap) :
  HeightmapSelector(window, selectedHeightmap, glm::ivec2(1))
{
}

HeightmapSelector::HeightmapSelector(std::shared_ptr<Window> window, std::shared_ptr<Heightmap> heightmap, const glm::ivec2& size):
  Component(window),
  _renderedSelector(window, size),
  _selectedHeightmap(heightmap)
{
  setColor(Color((Uint8)0, 0, 0, 80));
}

void HeightmapSelector::updateVisuals(int msElapsed, const Camera* camera) {
  if (_autoUpdatePointedPos && (!ImGui::GetCurrentContext() || !ImGui::GetIO().WantCaptureMouse)) {
    glm::ivec2 currentCursorpos;
    SDL_GetMouseState(&currentCursorpos.x, &currentCursorpos.y);
    setPointedPos(camera->screenToWorldPos(currentCursorpos));
  }

  updateSelectorHeights();
  _renderedSelector.updateVisuals(msElapsed, camera);
}

void HeightmapSelector::render(const Camera* camera) const {
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  _renderedSelector.render(camera);

  glDisable(GL_BLEND);
}

void HeightmapSelector::setPointedPos(const glm::vec2& pointedPos) {
  _renderedSelector.setOriginOffset(glm::vec3((int)pointedPos.x - (int)(getSize().x / 2.f), (int)pointedPos.y - (int)(getSize().y / 2.f), _selectedHeightmap->getOriginOffset().z + 0.01f));
}

const std::vector<float>& HeightmapSelector::updateSelectorHeights() {
  const std::vector<float>& selectedHeights = _selectedHeightmap->getHeights();

  for (int i = 0; i < getNbVertices().x; i++) {
    for (int j = 0; j < getNbVertices().y; j++) {
      glm::vec2 currentCoord = glm::vec2(getOriginOffset().x + i, getOriginOffset().y + j);

      if (!_selectedHeightmap->areInvalidVertexCoordinates(currentCoord))
        _renderedSelector.setHeight(glm::ivec2(i, j), selectedHeights[(int)currentCoord.x * _selectedHeightmap->getNbVertices().y + (int)currentCoord.y]);
    }
  }

  return _renderedSelector.getHeights();
}

void HeightmapSelector::setHeights(std::vector<float> heights) {
  _renderedSelector.setHeights(std::move(heights));

  for (int i = 0; i < getNbVertices().x; i++) {
    for (int j = 0; j < getNbVertices().y; j++) {
      glm::ivec2 currentCoord = glm::ivec2((int)getOriginOffset().x + i, (int)getOriginOffset().y + j);

      _selectedHeightmap->setHeight(currentCoord, _renderedSelector.getHeights()[i * getNbVertices().y + j]);
    }
  }
}

void HeightmapSelector::setPointedColor(const Color& color) {
  for (int i = 0; i < getNbVertices().x - 1; i++) {
    for (int j = 0; j < getNbVertices().y - 1; j++) {
      glm::ivec2 currentCoord = glm::ivec2((int)getOriginOffset().x + i, (int)getOriginOffset().y + j);

      _selectedHeightmap->setColor(currentCoord, color);
    }
  }
}

void HeightmapSelector::setSize(const glm::ivec2& size) {
  if (size != getSize()) {
    glm::vec2 centerPoint = getPointedPos();
    _renderedSelector.resize(size);
    setColor(Color((Uint8)0, 0, 0, 80));
    setPointedPos(centerPoint);
  }
}

#include <pybind11/stl.h>

void HeightmapSelector::pythonBindings(py::module& m) {
  py::class_<HeightmapSelector, std::shared_ptr<HeightmapSelector>, Component>(m, "HeightmapSelector")
    .def(py::init<std::shared_ptr<Window>, std::shared_ptr<Heightmap>>())
    .def(py::init<std::shared_ptr<Window>, std::shared_ptr<Heightmap>, const glm::ivec2&>())
    .def_readwrite("autoUpdatePointedPos", &HeightmapSelector::_autoUpdatePointedPos)
    .def_property("pointedPos", &HeightmapSelector::getPointedPos, &HeightmapSelector::setPointedPos)
    .def("getHeights", &HeightmapSelector::updateSelectorHeights)
    .def("setHeights", &HeightmapSelector::setHeights)
    .def_property("color", &HeightmapSelector::getColor, &HeightmapSelector::setColor)
    .def("setPointedColor", &HeightmapSelector::setPointedColor)
    .def_property("size", &HeightmapSelector::getSize, &HeightmapSelector::setSize);
}