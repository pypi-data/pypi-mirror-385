#include "UnitSelector.h"

#include "ColoredRectangles.h"
#include "HeightmapCamera.h"
#include "EventManager.h"
#include "Unit.h"
#include "UnitManager.h"
#include "InGameText.h"
#include "UIManager.h"
#include "utils.h"
#include "Window.h"

#include <algorithm>

UnitSelector::UnitSelector(std::shared_ptr<Window> window, std::shared_ptr<UnitManager> unitManager) :
  Component(window),
  _unitManager(unitManager)
{}

void UnitSelector::updateVisuals(int /*msElapsed*/, const Camera* camera) {
  computeUnit2DCorners(camera);

  cleanUpSelection();

  if (_inGameText)
    _inGameText->clearText();
  _gaugesOfColor.clear();
  _outlinesRects.clear();
  _selectableRectangles.clear();

  glm::ivec2 gaugeSize = getScaledGaugeSize();

  for (std::weak_ptr<Unit> weakUnit : _selection) {
    // Just checking for still being valid as the selection has already been cleaned up in updateVisuals
    // Can't be done here as it's a non-const function
    if (std::shared_ptr<Unit> unit = weakUnit.lock()) {
      glm::ivec2 unitTopCenter = unit->getScreenTopCenter();

      if (unit->getShouldDisplayGauge()) {
        glm::ivec4 fillingRectangle(
          unitTopCenter.x - gaugeSize.x / 2.f,
          unitTopCenter.y - gaugeSize.x / 4.f,
          gaugeSize.x * unit->getDisplayablePercentageValue() / 100.f,
          gaugeSize.y
        );

        _gaugesOfColor[unit->getDisplayableValueColor()].push_back(fillingRectangle);

        _outlinesRects.push_back(glm::ivec4(
          unitTopCenter.x - gaugeSize.x / 2.f,
          unitTopCenter.y - gaugeSize.x / 4.f,
          gaugeSize.x,
          gaugeSize.y
        ));

        unitTopCenter.y += gaugeSize.y;
      }

      if (!unit->getDisplayableText().empty()) {
        // Lazily create the in-game text widget
        if (!_inGameText) {
          std::shared_ptr<UIManager> uiManager = getWindow()->getElementByClass<UIManager>();

          if (!uiManager)
            throw std::runtime_error("No UIManager attached to the window, cannot display in-game text");

          _inGameText = std::static_pointer_cast<InGameText>(uiManager->createElement(py::type::of<InGameText>()));
        }

        _inGameText->pushText(TextElement{ unit->getDisplayableText(), unitTopCenter, glm::vec2(0.5f, 1.f) });
      }

      if (_displayUnitSelectionHitboxes)
        _selectableRectangles.push_back(unit->getScreenRect());
    }
  }
}

void UnitSelector::render(const Camera* camera) const {
  if (_displayUnitSelectionHitboxes) {
    ColoredRectangles selectableRectanglesRenderer(glm::vec4(0, 0, 1, 1), _selectableRectangles, camera->getViewportSize(), false);
    selectableRectanglesRenderer.render();
  }

  for (auto& gaugeRectangles : _gaugesOfColor) {
    ColoredRectangles gaugeDisplay(gaugeRectangles.first, gaugeRectangles.second, camera->getViewportSize());
    gaugeDisplay.render();
  }
  
  ColoredRectangles outlines(glm::vec4(0, 0, 0, 1), _outlinesRects, camera->getViewportSize(), false);
  outlines.render();

  if (_displaySelectionRectangle) {
    glm::ivec4 absoluteRect;
    if (_selectionRectangle.z > 0) {
      absoluteRect.x = _selectionRectangle.x;
      absoluteRect.z = _selectionRectangle.z;
    }
    else {
      absoluteRect.x = _selectionRectangle.x + _selectionRectangle.z;
      absoluteRect.z = -_selectionRectangle.z;
    }

    if (_selectionRectangle.w > 0) {
      absoluteRect.y = _selectionRectangle.y;
      absoluteRect.w = _selectionRectangle.w;
    }
    else {
      absoluteRect.y = _selectionRectangle.y + _selectionRectangle.w;
      absoluteRect.w = -_selectionRectangle.w;
    }

    ColoredRectangles rectSelectDisplay(glm::vec4(1), absoluteRect, camera->getViewportSize(), false);
    rectSelectDisplay.render();
  }
}

std::shared_ptr<Unit> UnitSelector::getSelectableUnit(glm::ivec2 screenTarget, float leniency) const {
  std::vector<float> distancesToScreenTarget;

  std::vector<std::shared_ptr<Unit>> selectableUnits = _unitManager->getElementsByFilter(
    [this, screenTarget, leniency, &distancesToScreenTarget](const std::shared_ptr<Unit> unit) {
      if (!unit->canBeSelected())
        return false;

      float distanceToScreenTarget = ut::getRectangleCircleDistance(unit->getScreenRect(), screenTarget);

      if (distanceToScreenTarget > leniency)
        return false;

      distancesToScreenTarget.push_back(distanceToScreenTarget);
      return true;
    }
  );

  if (selectableUnits.size() == 0)
    return nullptr;

  std::shared_ptr<Unit> bestUnit = selectableUnits[0];
  float bestUnitDistanceToScreenTarget = distancesToScreenTarget[0];

  for (int i = 0; i < selectableUnits.size(); i++) {
    bool isCloserToSelection = distancesToScreenTarget[i] < bestUnitDistanceToScreenTarget;
    bool isAsCloseToSelectionButCloserToScreen = distancesToScreenTarget[i] == bestUnitDistanceToScreenTarget
      && selectableUnits[i]->getScreenDepth() < bestUnit->getScreenDepth();

    if (isCloserToSelection || isAsCloseToSelectionButCloserToScreen) {
      bestUnit = selectableUnits[i];
      bestUnitDistanceToScreenTarget = distancesToScreenTarget[i];
    }
  }

  return bestUnit;
}

void UnitSelector::select(const glm::ivec4& encompassingRectangle, bool add, const std::function<bool(const std::shared_ptr<Unit>)>& filter) {
  if (!add)
    _selection.clear();

  std::vector<std::shared_ptr<Unit>> selectableUnits = _unitManager->getElementsByFilter(
    [filter](const std::shared_ptr<Unit> unit) { return unit->canBeSelected() && filter(unit); }
  );

  std::vector<std::shared_ptr<Unit>> selection = getSelection();

  for (std::shared_ptr<Unit> unit : selectableUnits) {
    if (std::find(selection.begin(), selection.end(), unit) == selection.end()) {
      if (ut::getRectanglesIntersect(encompassingRectangle, unit->getScreenRect())) {
        _selection.push_back(unit);
      }
    }
  }
}

void UnitSelector::deleteOneInSelection() {
  cleanUpSelection();
  if (_selection.size() > 0)
    _selection[0].lock()->deleteElement();
}

void UnitSelector::goBackToSelection(HeightmapCamera* camera) {
  std::vector<std::shared_ptr<Unit>> selection = getSelection();
  
  if (!selection.empty()) {
    glm::vec2 barycenter(0);
    float nbSelected = 0;

    for (std::shared_ptr<Unit> element : selection) {
      barycenter += element->getPosition();
      nbSelected++;
    }

    camera->setAim2DPosition(barycenter / nbSelected);
  }
}

void UnitSelector::moveSelection(const glm::vec2& target) {
  for (std::shared_ptr<Unit> unit: getSelection()) {
    unit->setTarget(target);
  }
}

std::vector<std::shared_ptr<Unit>> UnitSelector::getSelection() {
  cleanUpSelection();

  std::vector<std::shared_ptr<Unit>> strongSelection;

  for (std::weak_ptr<Unit> weakElement : _selection) {
    strongSelection.push_back(weakElement.lock());
  }

  return strongSelection;
}

glm::ivec2 UnitSelector::getScaledGaugeSize() const {
  float DPIZoom = getWindow()->getDPIZoom();
  return glm::ivec2((int)(_gaugeSize.x * DPIZoom + 0.5f), (int)(_gaugeSize.y * DPIZoom + 0.5f));
}

void UnitSelector::cleanUpSelection() {
  std::erase_if(_selection, [](std::weak_ptr<Unit>& unit) { 
    return unit.expired() || !unit.lock()->canBeSelected();
  });
}

void UnitSelector::computeUnit2DCorners(const Camera* camera) {
  glm::mat4 rotateUnits = _unitManager->getUnitRenderer().getModelMatrix(camera);

  for (auto unit : _unitManager->getElements()) {
    glm::vec3 pos;
    pos.x = unit->getPosition().x;
    pos.y = unit->getPosition().y;
    pos.z = unit->getHeight();

    std::array<float, 12> vertices;

    if (unit->canBeSelected() && glm::length(pos - camera->getCurrentPosition()) > _unitManager->getUnitRenderer().getUnitNearPlane()) {
      // Calculate new corners
      glm::vec3 corners3[4];
      const std::array<float, 12>& vert = unit->getVertices();

      corners3[0] = glm::vec3(vert[0], vert[1], vert[2]);
      corners3[1] = glm::vec3(vert[3], vert[4], vert[5]);
      corners3[2] = glm::vec3(vert[6], vert[7], vert[8]);
      corners3[3] = glm::vec3(vert[9], vert[10], vert[11]);

      glm::vec3 translatePosition(unit->getPosition().x,
        unit->getPosition().y,
        unit->getHeight());

      glm::mat4 model = glm::translate(glm::mat4(1.f), translatePosition) * rotateUnits;

      // Compute their projections
      for (int i = 0; i < 4; i++) {
        glm::vec4 tmp(corners3[i], 1.f);
        tmp = model * tmp;
        tmp = camera->getViewProjectionMatrix() * tmp;
        corners3[i] = glm::vec3(tmp) / tmp.w;
      }

      for (int i = 0; i < 4; i++) {
        vertices[3 * i] = corners3[i].x;
        vertices[3 * i + 1] = corners3[i].y;
        vertices[3 * i + 2] = corners3[i].z;
      }
    }

    else {
      for (int i = 0; i < 12; i++) {
        vertices[i] = 0;
      }
    }

    unit->setProjectedVertices(vertices);
  }
}

#include <pybind11/functional.h>
#include <pybind11/stl.h>

void UnitSelector::pythonBindings(py::module& m) {
  py::class_<UnitSelector, std::shared_ptr<UnitSelector>, Component>(m, "UnitSelector")
    .def(py::init<std::shared_ptr<Window>, std::shared_ptr<UnitManager>>())
    .def("getSelectableUnit", &UnitSelector::getSelectableUnit)
    .def("select", py::overload_cast<const glm::ivec4&, bool>(&UnitSelector::select))
    .def("select", py::overload_cast<const glm::ivec4&, bool, const std::function<bool(const std::shared_ptr<Unit>)> &>(& UnitSelector::select))
    .def("clearSelection", &UnitSelector::clearSelection)
    .def("isSelectionEmpty", &UnitSelector::isSelectionEmpty)
    .def("addToSelection", &UnitSelector::addToSelection)
    .def("removeFromSelection", &UnitSelector::removeFromSelection)
    .def("deleteOneInSelection", &UnitSelector::deleteOneInSelection)
    .def("goBackToSelection", &UnitSelector::goBackToSelection)
    .def("moveSelection", &UnitSelector::moveSelection)
    .def_property_readonly("selection", &UnitSelector::getSelection)
    .def_readwrite("selectionRectangle", &UnitSelector::_selectionRectangle)
    .def_readwrite("gaugeSize", &UnitSelector::_gaugeSize)
    .def_readwrite("displaySelectionRectangle", &UnitSelector::_displaySelectionRectangle)
    .def_readwrite("displayUnitSelectionHitboxes", &UnitSelector::_displayUnitSelectionHitboxes);
}