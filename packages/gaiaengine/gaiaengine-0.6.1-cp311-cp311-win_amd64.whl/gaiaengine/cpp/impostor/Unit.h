#pragma once

#include <glm/glm.hpp>

#include "Delegate.h"
#include "Manager.h"
#include "TargetInterface.h"

#include <array>
#include <memory>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Heightmap;
class UnitAsset;
class UnitManager;
class AnimatedUnitAsset;
class TextureArray;
class Window;

class Unit : public ManagedElement, public TargetInterface {
public:
  Unit(std::shared_ptr<UnitManager> unitManager, std::shared_ptr<const UnitAsset> unitAsset, glm::vec2 position);
  virtual ~Unit() = default;

  void update(int msElapsed, const Heightmap* heightmap); // Update pos and inner statuses
  void updateDisplay(float theta); // Update sprite

  void startAnimation(int animation);
  void startAnimation(int animation, float playbackSpeed);
  // The callback is expected to be a python function without arguments
  void startAnimation(int animation, const py::function& animFinishedCallback);
  void startAnimation(int animation, float playbackSpeed, const py::function& animFinishedCallback);

  void deleteElement() override;

  inline std::vector<std::shared_ptr<Unit>> getVisibleUnits() const;

  // TargetInterface
  glm::vec2 getScaledDirection() const override { return _speed * _direction; }
  glm::vec2 getPosition() const override { return _position; }
  bool isValid() const override { return !isElementDeleted(); }

  bool hasReachedTarget() const;
  void stopMoving() { _speed = 0.f; _onStoppedMoving.broadcast(); }

  // Getters and setters

  std::shared_ptr<UnitManager> getUnitManager() const;

  const TextureArray* getTextureArray() const;
  inline std::shared_ptr<const UnitAsset> getUnitAsset() const { return _unitAsset; }

  void setPosition(const glm::vec2& val);

  float getSpeed() const { return _speed; }
  inline void setSpeed(float newSpeed) { _speed = newSpeed; }

  inline glm::vec2 getDirection() const { return _direction; }
  // Setting the direction makes you forget about the target
  virtual void setDirection(const glm::vec2& direction);

  inline float getOrientation() const { return _orientation; }
  void setOrientation(float nOrientation);

  bool isAnimationLoaded(int animation);

  // React to the environment
  virtual void setTarget(const glm::vec2& target);
  void setTarget(std::shared_ptr<Unit> target);
  glm::vec2 getTargetPosition() const;

  inline void setHeight(float height) { _height = height; setPositionArray(); }
  inline float getHeight() const { return _height; }

  inline const std::array<float, 12>& getVertices()        const {return _vertices;}
  inline const std::array<float, 12>& getPositionArray()   const {return _posArray;}
  inline const std::array<float,  8>& getCoord2D()         const {return _coord2D;}
  inline const std::array<float,  4>& getLayer()           const {return _layer;}
  inline const std::array<float, 12>& getHeightmapNormal() const {return _heightmapNormal;}

  inline void setProjectedVertices(std::array<float, 12> nVertices) { _projectedVertices = nVertices; }
  // x y are the screen coordinates of the top left corner of the sprite ((0,0) being on the top left corner of the window
  // z w are the extent of the sprite
  glm::ivec4 getScreenRect() const;
  
  // Returns how far away from the camera the unit is
  inline float getScreenDepth() const { return _projectedVertices[2]; }
  
  // Gets the screen position that will match the highest sprite height throughout all animations, aligned horizontally with the anchor
  glm::ivec2 getScreenTopCenter() const;

  inline int getType() const { return _type; }
  // Resets the line of sight to the base one of the new type
  void setType(int val);

  inline float getLineOfSight() const { return _lineOfSight; }
  void setLineOfSight(float val) { _lineOfSight = val; }

  inline bool canBeSelected() const { return !isElementDeleted() && _canBeSelected; }

  inline float getDisplayablePercentageValue() const { return _displayablePercentageValue; }
  inline glm::vec4 getDisplayableValueColor() const { return _displayableValueColor; }
  inline bool getShouldDisplayGauge() const { return _shouldDisplayGauge; }
  inline std::string getDisplayableText() const { return _displayableText; }

  inline int getCurrentSprite() const { return _currentSprite; }
  void setCurrentSprite(int val);

  inline int getCurrentTexture() const { return static_cast<int>(_layer[0]); }
  void setCurrentTexture(int val);

  void setHeightmapNormal(const glm::vec3& val);

  int getNumSprites() const;
  int getNumTextures() const;

  static void pythonBindings(py::module& m);

  inline float getSizeFactor() const { return _sizeFactor; }
  inline void setSizeFactor(float val) { _sizeFactor = val; setCurrentSprite(getCurrentSprite()); }

private:
  void setDirectionInternal(const glm::vec2& direction);
  void updateAnimation(int msElapsed);

  void setPositionArray();

  std::shared_ptr<const UnitAsset> _unitAsset;
  float _sizeFactor = 1.f;

  // The type allows to set which unit can be visible to which other, 
  // as well as having different navigation channels.
  // -1 is the default, where no type is defined (non-detectable, can navigate on anything)
  int _type = -1;
  float _lineOfSight = 0.f;

  glm::vec2 _position = glm::vec2(0);
  float _height = 0.f;

  bool _canBeSelected = false;
  float _displayablePercentageValue = 0.f;
  glm::vec4 _displayableValueColor = glm::vec4(0);
  bool _shouldDisplayGauge = true;
  std::string _displayableText;

  float _speed = 0.f;
  std::shared_ptr<TargetInterface> _target;
  float _targetAcceptanceRadius = 0.5f;
  bool _stopOnReachTarget = false;
  // Normalized vector towards the target
  // It is private to guarantee a correct normalization
  glm::vec2 _direction = glm::vec2(0.f);

  py::function _onAnimFinished;

  float _camOrientation = 0.f;
  float _orientation = 0.f; // Angle between the front of the sprite and the camera

  // Animation variables
  std::shared_ptr<const AnimatedUnitAsset> _animationAsset = nullptr;
  int _currentAnimationOrientation = -1;
  int _currentAnimFrame = -1;
  int _msAnimationElapsed = 0;
  bool _animPaused = false;
  float _animPlaybackSpeed = 1.f;

  Delegate _onTargetOrDirectionSet;
  Delegate _onStoppedMoving;
  Delegate _onTeleported;

  std::array<float, 12> _vertices{};
  std::array<float, 12> _posArray{};
  std::array<float,  8> _coord2D{};
  std::array<float,  4> _layer{};
  std::array<float, 12> _heightmapNormal{};
  std::array<float, 12> _projectedVertices{};

private:
  int _currentSprite = -1;
};
