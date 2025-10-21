#include "UnitManager.h"

#include <glm/gtx/vector_angle.hpp>

#include "Camera.h"
#include "Heightmap.h"
#include "UnitAsset.h"
#include "Unit.h"
#include "Window.h"

#include <algorithm>
#include <sstream>

UnitManager::UnitManager(std::shared_ptr<Window> window, std::shared_ptr<Heightmap> heightmap) :
  Component(window),
  _heightmap(heightmap)
{}

void UnitManager::update(int msElapsed) {
  for (auto& unit: getElements()) {
    unit->update(msElapsed, _heightmap.get());
  }

  updateSpatialOrders();
}

void UnitManager::updateVisuals(int /*msElapsed*/, const Camera* camera) {
  float cameraAngleWithXAxis = glm::degrees(glm::orientedAngle(glm::vec2(1.f, 0.f), glm::normalize(-glm::vec2(camera->getCurrentDirection()))));

  for (auto& unit: getElements()) {
    unit->updateDisplay(cameraAngleWithXAxis);
    unit->setHeightmapNormal(_heightmap->getCellNormal(unit->getPosition()));
  }

  _unitRenderer.loadUnits(getElements());
}

void UnitManager::render(const Camera* camera) const {
  _unitRenderer.render(camera);
}

std::shared_ptr<Unit> UnitManager::createElement(const py::object& myClass, const py::args& args /*= py::args()*/) {
  UnitAsset* unitAsset = args[0].cast<UnitAsset*>();

  if (unitAsset == nullptr)
    throw std::invalid_argument("Invalid UnitAsset object");

  if (!unitAsset->isLoaded())
    unitAsset->load();

  std::shared_ptr<Unit> newUnit = Manager<Unit>::createElement(myClass, args);

  // If the new unit has a bigger line of sight than the one that has been used to compute the spatial orders,
  // we need to recompute all of them
  if (getVisibleTypes(newUnit->getType()).size() > 0) {
    if (newUnit->getLineOfSight() > _unitTypeToSpatialOrder[newUnit->getType()].maxLineOfSight) {
      updateSpatialOrders();
      return newUnit;
    }
  }

  // Otherwise just add it to the existing spatial orders
  addUnitToSpatialOrders(newUnit);
  return newUnit;
}

float UnitManager::getHeight(const glm::vec2& pos) const {
  return _heightmap->getHeight(pos);
}

std::vector<std::shared_ptr<Unit>> UnitManager::getVisibleUnits(const glm::vec2& pos, int type, float lineOfSight) const {
  const UnitSpatialOrder* spatialOrder = nullptr;
  try {
    spatialOrder = &_unitTypeToSpatialOrder.at(type);
  }
  catch (const std::out_of_range&) {
    throw std::out_of_range(std::string("No visible types set for type ") + std::to_string(type));
  }

  glm::vec2 cellSize = glm::vec2(spatialOrder->maxLineOfSight);
  glm::ivec2 nbCells = glm::ivec2(_heightmap->getMaxCoordinates() / cellSize) + glm::ivec2(1); // +1 for border cells

  std::vector<std::shared_ptr<Unit>> visibleUnits;

  glm::ivec2 currentCell = pos / cellSize;
  float lineOfSightSquared = lineOfSight * lineOfSight;

  for (int i = std::max(0, currentCell.x - 1); i <= std::min(nbCells.x - 1, currentCell.x + 1); i++) {
    for (int j = std::max(0, currentCell.y - 1); j <= std::min(nbCells.y - 1, currentCell.y + 1); j++) {
      glm::ivec2 cellCoords(i, j);

      const auto& unitsInCell = spatialOrder->grid.find(cellCoords);
      if (unitsInCell != spatialOrder->grid.end()) {
        auto isUnitVisible = [pos, lineOfSightSquared](std::shared_ptr<Unit> unit) {
          return glm::distance2(pos, unit->getPosition()) <= lineOfSightSquared;
        };
        
        std::copy_if(unitsInCell->second.begin(), unitsInCell->second.end(), std::back_inserter(visibleUnits), isUnitVisible);
      }
    }
  }

  return visibleUnits;
}

const std::vector<int>& UnitManager::getVisibleTypes(int typeWatching) const {
  static const std::vector<int> defaultEmptyVector;
  const auto& spatialOrderPair = _unitTypeToSpatialOrder.find(typeWatching);
 
  if (spatialOrderPair == _unitTypeToSpatialOrder.end())
    return defaultEmptyVector;

  return spatialOrderPair->second.visibleTypes;
}

float UnitManager::getBaseLineOfSight(int typeWatching) const {
  const auto& spatialOrderPair = _unitTypeToSpatialOrder.find(typeWatching);

  if (spatialOrderPair == _unitTypeToSpatialOrder.end())
    return 0.f;

  return spatialOrderPair->second.baseLineOfSight;
}

void UnitManager::setVisibleTypes(int typeWatching, const std::vector<int>& visibleTypes, float baseLineOfSight) {
  _unitTypeToSpatialOrder[typeWatching].visibleTypes = visibleTypes;
  _unitTypeToSpatialOrder[typeWatching].baseLineOfSight = baseLineOfSight;

  if (baseLineOfSight > _unitTypeToSpatialOrder[typeWatching].maxLineOfSight)
    _unitTypeToSpatialOrder[typeWatching].maxLineOfSight = baseLineOfSight;

  updateSpatialOrders();
}

void UnitManager::updateSpatialOrders() {
  // Updating line of sight values
  for (auto& spatialOrderPair : _unitTypeToSpatialOrder) {
    spatialOrderPair.second.maxLineOfSight = 0.f;
  }

  for (auto& unit : getElements()) {
    if (getVisibleTypes(unit->getType()).size() > 0)
      if (unit->getLineOfSight() > _unitTypeToSpatialOrder[unit->getType()].maxLineOfSight)
        _unitTypeToSpatialOrder.at(unit->getType()).maxLineOfSight = unit->getLineOfSight();
  }

  // Updating which type is visible from which
  _typeVisibleFromTheseTypes.clear();

  for (auto& spatialOrderPair : _unitTypeToSpatialOrder) {
    spatialOrderPair.second.grid.clear();
    if (spatialOrderPair.second.maxLineOfSight > 0.f) {
      for (int visibleType : spatialOrderPair.second.visibleTypes) {
        _typeVisibleFromTheseTypes[visibleType].push_back(spatialOrderPair.first);
      }
    }
  }

  // Actually sorting the units
  for (auto& unit : getElements()) {
    addUnitToSpatialOrders(unit);
  }
}

void UnitManager::addUnitToSpatialOrders(std::shared_ptr<Unit> unit) {
  const auto& visibleFromTheseTypes = _typeVisibleFromTheseTypes.find(unit->getType());
  if (visibleFromTheseTypes != _typeVisibleFromTheseTypes.end()) {
    for (int typeWatching : visibleFromTheseTypes->second) {
      glm::ivec2 cell = glm::ivec2(unit->getPosition() / glm::vec2(_unitTypeToSpatialOrder.at(typeWatching).maxLineOfSight));
      _unitTypeToSpatialOrder.at(typeWatching).grid[cell].push_back(unit);
    }
  }
}

#include <pybind11/stl.h>

void UnitManager::pythonBindings(py::module& m) {
  py::class_<UnitManager, std::shared_ptr<UnitManager>, Component, ManagerBase>(m, "UnitManager", py::multiple_inheritance())
    .def(py::init< std::shared_ptr<Window>, std::shared_ptr<Heightmap>>())
    .def("getVisibleUnits", &UnitManager::getVisibleUnits)
    .def("getVisibleTypes", &UnitManager::getVisibleTypes)
    .def("setVisibleTypes", &UnitManager::setVisibleTypes)
    .def_readwrite("heightmap", &UnitManager::_heightmap)
    .def_readwrite("baseUnitSizeFactor", &UnitManager::_baseUnitSizeFactor)
    .def_readwrite("unitsCanWrapAroundWorld", &UnitManager::_unitsCanWrapAroundWorld);
}
