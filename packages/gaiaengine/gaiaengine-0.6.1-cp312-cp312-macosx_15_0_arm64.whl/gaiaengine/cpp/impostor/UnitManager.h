#pragma once

#include <glm/glm.hpp>
#include <glm/gtx/hash.hpp>

#include "Component.h"
#include "Unit.h"
#include "UnitRenderer.h"
#include "Manager.h"

#include <list>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

class Camera;
class Heightmap;
class TextureArray;


typedef std::unordered_map < glm::ivec2, std::list < std::shared_ptr< Unit> > > Grid;

typedef struct UnitSpatialOrder {
  // Saved as base characteristics of unit types
  std::vector<int> visibleTypes;

  // Re-built every frame to make queries of surrounding units faster
  float maxLineOfSight = 0.f;
  float baseLineOfSight = 0.f;
  Grid grid;
} UnitSpatialOrder;


class UnitManager: public Component, public Manager<Unit> {
public:
  UnitManager(std::shared_ptr<Window> window, std::shared_ptr<Heightmap> heightmap);
  
  void update(int msElapsed) override;
  void updateVisuals(int msElapsed, const Camera* camera) override;
  void render(const Camera* camera) const override;

  std::shared_ptr<Unit> createElement(const py::object& myClass, const py::args& args = py::args()) override;

  const UnitRenderer& getUnitRenderer() const { return _unitRenderer; }

  float getHeight(const glm::vec2& pos) const;

  inline float getBaseUnitSizeFactor() const { return _baseUnitSizeFactor; }

  inline bool getUnitsCanWrapAroundWorld() const { return _unitsCanWrapAroundWorld; }

  std::vector<std::shared_ptr<Unit>> getVisibleUnits(const glm::vec2& pos, int type, float lineOfSight) const;

  const std::vector<int>& getVisibleTypes(int typeWatching) const;
  float getBaseLineOfSight(int typeWatching) const;
  void setVisibleTypes(int typeWatching, const std::vector<int>& visibleTypes, float baseLineOfSight);

  static void pythonBindings(py::module& m);
private:
  std::unordered_map<int, UnitSpatialOrder> _unitTypeToSpatialOrder;
  std::unordered_map<int, std::vector<int>> _typeVisibleFromTheseTypes;

  void updateSpatialOrders();
  void addUnitToSpatialOrders(std::shared_ptr<Unit> unit);

  std::shared_ptr<Heightmap> _heightmap;
  float _baseUnitSizeFactor = 1.f;
  bool _unitsCanWrapAroundWorld = false;

  UnitRenderer _unitRenderer;
};

