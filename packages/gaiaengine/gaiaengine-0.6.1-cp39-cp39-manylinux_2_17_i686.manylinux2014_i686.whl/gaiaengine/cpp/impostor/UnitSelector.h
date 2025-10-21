#pragma once

#include <glm/glm.hpp>
#include <glm/gtx/hash.hpp>

#include "Component.h"

#include <functional>
#include <memory>
#include <unordered_map>
#include <vector>

class Camera;
class HeightmapCamera;
class Unit;
class UnitManager;
class InGameText;

class UnitSelector : public Component {
public:
  UnitSelector(std::shared_ptr<Window> window, std::shared_ptr<UnitManager> unitManager);

  void updateVisuals(int msElapsed, const Camera* camera) override;
  void render(const Camera* camera) const override;

  std::shared_ptr<Unit> getSelectableUnit(glm::ivec2 screenTarget, float leniency) const;
  void select(const glm::ivec4& encompassingRectangle, bool add, const std::function<bool(const std::shared_ptr<Unit>)>& filter);
  inline void select(const glm::ivec4& encompassingRectangle, bool add) {
    select(encompassingRectangle, add, [](const std::shared_ptr<Unit>) { return true; });
  }

  inline void clearSelection() { _selection.clear(); }
  inline bool isSelectionEmpty() { cleanUpSelection(); return _selection.empty(); }
  inline void addToSelection(std::shared_ptr<Unit> unit) { _selection.push_back(unit); }
  inline void removeFromSelection(std::shared_ptr<Unit> unit) {
    std::erase_if(_selection, [unit](std::weak_ptr<Unit> it) { return it.lock() == unit; });
  }
  void deleteOneInSelection();
  void goBackToSelection(HeightmapCamera* camera);
  void moveSelection(const glm::vec2& target);

  std::vector<std::shared_ptr<Unit>> getSelection();

  glm::ivec2 getScaledGaugeSize() const;

  static void pythonBindings(py::module& m);

private:
  // Remove stale elements from the selection
  void cleanUpSelection();

  void computeUnit2DCorners(const Camera* camera);

  std::shared_ptr<UnitManager> _unitManager;
  std::shared_ptr<InGameText> _inGameText;

  glm::ivec4 _selectionRectangle = glm::ivec4(-1);

  // For each color, store the list of rectangles that will fill the gauge
  std::unordered_map<glm::vec4, std::vector<glm::ivec4>> _gaugesOfColor;
  std::vector<glm::ivec4> _outlinesRects;
  std::vector<glm::ivec4> _selectableRectangles;

  glm::ivec2 _gaugeSize = glm::ivec2(20, 4);

  bool _displayUnitSelectionHitboxes = false;
  bool _displaySelectionRectangle = false;

  std::vector<std::weak_ptr<Unit>> _selection;
};
