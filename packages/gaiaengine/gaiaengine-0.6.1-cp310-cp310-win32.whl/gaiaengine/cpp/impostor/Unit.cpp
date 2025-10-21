#include "Unit.h"

#include <glm/gtx/vector_angle.hpp>

#include "Heightmap.h"
#include "UnitAsset.h"
#include "UnitManager.h"
#include "AnimatedUnitAsset.h"
#include "TextureArray.h"
#include "Window.h"

#include <cmath>

Unit::Unit(std::shared_ptr<UnitManager> unitManager, std::shared_ptr<const UnitAsset> unitAsset, glm::vec2 position) :
  ManagedElement(unitManager),
  _unitAsset(unitAsset),
  _sizeFactor(unitManager->getBaseUnitSizeFactor()),
  _orientation(rand() / (float)RAND_MAX * 360.f),
  _animationAsset(std::dynamic_pointer_cast<const AnimatedUnitAsset>(unitAsset))
{
  setPosition(position);

  setCurrentTexture(0);
  setCurrentSprite(rand() % _unitAsset->getSpriteInfo()[0].size());

  if (_animationAsset) {
    _canBeSelected = true;
    startAnimation(0);
  }
}

void Unit::update(int msElapsed, const Heightmap* heightmap) {
  float cappedSpeed = _speed;

  if (_target) {
    if (!_target->isValid()) {
      stopMoving();
      _stopOnReachTarget = false;
      _target.reset();
    }
    else if (_stopOnReachTarget && hasReachedTarget()) {
      stopMoving();
      _stopOnReachTarget = false;
    }
    else {
      setDirectionInternal(_target->getPosition() - _position);
      if (hasReachedTarget())
        // Making sure we don't continue moving too fast towards the target if it's not going away
        cappedSpeed = std::min(std::sqrt(std::max(0.f, glm::dot(_target->getScaledDirection(), _direction))), _speed);
    }
  }

  // Don't update the position if the direction is invalid
  if (_direction != glm::vec2(0.f)) {
    glm::vec2 newPos = _position + _direction * cappedSpeed * (msElapsed / 1000.f);

    bool hasTeleported = false;
    glm::vec2 teleportTriggerPosition(-1);

    if (getUnitManager()->getUnitsCanWrapAroundWorld()) {
      teleportTriggerPosition = newPos;
      hasTeleported = heightmap->teleportPositionOnOtherSideIfOutside(newPos);
    }

    if (heightmap->getIsNavigable(newPos)) {
      _position = newPos;
      _height = heightmap->getHeight(_position);
    }
    else
      stopMoving();

    if (hasTeleported)
      _onTeleported.broadcast(py::make_tuple(teleportTriggerPosition));

    setPositionArray();
  }

  updateAnimation(msElapsed);
}

void Unit::updateDisplay(float theta) {
  setOrientation(_orientation + _camOrientation - theta); // Orientation moves opposite to the camera
  _camOrientation = theta;

  if (_direction.x != 0.f || _direction.y != 0.f) {
    float ori = glm::degrees(glm::orientedAngle(glm::vec2(1.0f, 0.0f), _direction));
    setOrientation(ori - _camOrientation);
  }

  if (_animationAsset) {
    _currentAnimationOrientation = _animationAsset->getClosestOrientation(getOrientation());
    setCurrentSprite(_currentAnimationOrientation * _animationAsset->getNbSteps(getCurrentTexture()) + _currentAnimFrame);
  }
}


void Unit::startAnimation(int animation) {
  startAnimation(animation, 1.f, py::function());
}

void Unit::startAnimation(int animation, float playbackSpeed) {
  startAnimation(animation, playbackSpeed, py::function());
}

void Unit::startAnimation(int animation, const py::function& animFinishedCallback) {
  startAnimation(animation, 1.f, animFinishedCallback);
}

void Unit::startAnimation(int animation, float playbackSpeed, const py::function& animFinishedCallback) {
  if (isElementDeleted())
    return;

  if (!_animationAsset)
    throw std::runtime_error("No animation asset has been specified");

  if (!isAnimationLoaded(animation))
    throw std::out_of_range("Trying to start an animation whose asset hasn't been loaded");

  setCurrentTexture(animation);
  setCurrentSprite(_animationAsset->getClosestOrientation(getOrientation()) * _animationAsset->getNbSteps(getCurrentTexture()));

  _currentAnimFrame = 0;
  _msAnimationElapsed = 0;
  _animPaused = false;

  _animPlaybackSpeed = playbackSpeed;
  _onAnimFinished = animFinishedCallback;
}

void Unit::deleteElement() {
  if (!isElementDeleted()) {
    _onAnimFinished = py::function();
    _onTargetOrDirectionSet.deactivate();
    _onStoppedMoving.deactivate();
    _onTeleported.deactivate();
  }

  ManagedElement::deleteElement();
}

void Unit::setPosition(const glm::vec2& val) {
  _position = val;
  setHeight(getUnitManager()->getHeight(_position));
}

std::shared_ptr<UnitManager> Unit::getUnitManager() const {
  return std::static_pointer_cast<UnitManager>(getManager());
}

std::vector<std::shared_ptr<Unit>> Unit::getVisibleUnits() const {
  return getUnitManager()->getVisibleUnits(_position, _type, _lineOfSight);
}

const TextureArray* Unit::getTextureArray() const {
  return _unitAsset->getTextureArray();
}

bool Unit::hasReachedTarget() const {
  if (!_target)
    return false;

  return glm::length2(_target->getPosition() - _position) < _targetAcceptanceRadius * _targetAcceptanceRadius;
}

void Unit::setTarget(const glm::vec2& target) {
  _target = std::make_shared<StaticTarget>(target);
  _stopOnReachTarget = true;
  setDirectionInternal(_target->getPosition() - _position);
  if (_speed == 0.f)
    _onTargetOrDirectionSet.broadcast();
}

void Unit::setTarget(std::shared_ptr<Unit> target) {
  _target = target;
  // By default, a Unit will follow an Unit target instead of stopping when reached
  _stopOnReachTarget = false;
  if (_target)
    setDirectionInternal(_target->getPosition() - _position);
  if (_speed == 0.f)
    _onTargetOrDirectionSet.broadcast();
}

glm::vec2 Unit::getTargetPosition() const {
  if (!_target)
    throw std::runtime_error("No valid target");

  return _target->getPosition();
}

void Unit::setDirection(const glm::vec2& direction) {
  setDirectionInternal(direction);
  _stopOnReachTarget = false;
  _target.reset();
  if (_speed == 0.f)
    _onTargetOrDirectionSet.broadcast();
}

void Unit::setDirectionInternal(const glm::vec2& direction) {
  // Only setting the direction if it's not going to be NaN.
  if (direction != glm::vec2(0.f))
    _direction = glm::normalize(direction);
  else
    _direction = direction;
}

void Unit::setOrientation(float nOrientation) {
  _orientation = nOrientation;

  if (_orientation < 0.f)
    _orientation += 360.f + 360 * (int)(-_orientation / 360);
  else
    _orientation -= 360.f * (int)(_orientation / 360);
}

bool Unit::isAnimationLoaded(int animation) {
  return _animationAsset && _animationAsset->textureExists(animation);
}

void Unit::updateAnimation(int msElapsed) {
  if (_animPlaybackSpeed == 0.0 || _animPaused || !_animationAsset)
    return;

  int steps = _animationAsset->getNbSteps(getCurrentTexture());
  int frameDuration = (int)(_animationAsset->getFrameDurationMs(getCurrentTexture()) / _animPlaybackSpeed);
  int msPause = _animationAsset->getReplayDelay(getCurrentTexture());
  _msAnimationElapsed += msElapsed;

  // We make sure that the elapsed time does not extend one loop
  int msTotalAnimDuration = steps * frameDuration + msPause;
  _msAnimationElapsed = msTotalAnimDuration != 0 ? _msAnimationElapsed % msTotalAnimDuration : _msAnimationElapsed;

  int nextSprite = _currentAnimFrame + _msAnimationElapsed / frameDuration;

  // Simple case, no restart to handle
  if (nextSprite < steps) {
    _msAnimationElapsed -= (nextSprite - _currentAnimFrame) * frameDuration;
    _currentAnimFrame = nextSprite;
  }

  else {
    _msAnimationElapsed -= (steps - 1 - _currentAnimFrame) * frameDuration;

    // The sprite is in the pause
    if (_msAnimationElapsed < msPause)
      _currentAnimFrame = steps - 1;

    // The sprite has started a new loop
    else {
      if (_onAnimFinished)
        _onAnimFinished();

      // Only if no animation was launched by the callback
      if (_msAnimationElapsed != 0) {
        _msAnimationElapsed -= msPause;
        nextSprite = _msAnimationElapsed / frameDuration;
        _msAnimationElapsed -= nextSprite * frameDuration;
        _currentAnimFrame = nextSprite;
      }
    }
  }
}

glm::ivec4 Unit::getScreenRect() const {
  glm::ivec2 screenSize = getWindow()->getWindowSize();
  glm::ivec4 res;
  res.x = (int) ( (_projectedVertices[3] + 1.f) / 2.f * screenSize.x);
  res.y = (int) (-(_projectedVertices[1] + 1.f) / 2.f * screenSize.y + screenSize.y);
  res.z = (int) ( (_projectedVertices[0] - _projectedVertices[3]) / 2.f * screenSize.x);
  res.w = (int) ( (_projectedVertices[1] - _projectedVertices[7]) / 2.f * screenSize.y);

  return res;
}

glm::ivec2 Unit::getScreenTopCenter() const {
  glm::ivec4 corners = getScreenRect();
  const SpriteInfo& currentSprite = _unitAsset->getCurrentSpriteInfo(getCurrentTexture(), getCurrentSprite());
  
  return glm::ivec2(corners.x + std::round(currentSprite.anchor_x * std::abs(corners.z) / (float)std::abs(currentSprite.w)),
                    corners.y + std::round((currentSprite.anchor_y - _unitAsset->getMaxAnchorHeight()) * std::abs(corners.w) / (float)std::abs(currentSprite.h)));
}

void Unit::setType(int val) {
  _type = val;
  _lineOfSight = getUnitManager()->getBaseLineOfSight(_type);
}

void Unit::setPositionArray() {
  for (int i = 0; i < 4; i++) {
    _posArray[3*i]     = _position.x;
    _posArray[3*i + 1] = _position.y;
    _posArray[3*i + 2] = _height;
  }
}

void Unit::setCurrentSprite(int sprite) {
  _currentSprite = sprite;

  glm::vec4 rect = _unitAsset->getTexRectangle(getCurrentTexture(), sprite);

  _coord2D[0] = rect.x + rect.z;
  _coord2D[1] = rect.y;
  _coord2D[2] = rect.x;
  _coord2D[3] = rect.y;
  _coord2D[4] = rect.x;
  _coord2D[5] = rect.y + rect.w;
  _coord2D[6] = rect.x + rect.z;
  _coord2D[7] = rect.y + rect.w;

  const SpriteInfo& currentSprite = _unitAsset->getCurrentSpriteInfo(getCurrentTexture(), getCurrentSprite());
  glm::vec2 size = glm::vec2(std::abs(currentSprite.w), std::abs(currentSprite.h)) * _sizeFactor;

  // The anchor is based on the top left corner of the texture, while we're drawing from the bottom left
  glm::vec2 offset = glm::vec2(-currentSprite.anchor_x, currentSprite.anchor_y - std::abs(currentSprite.h)) * _sizeFactor;

  _vertices[0] = 0; _vertices[1] =  offset.x + size.x; _vertices[2] =  offset.y + size.y;
  _vertices[3] = 0; _vertices[4] =  offset.x;          _vertices[5] =  offset.y + size.y;
  _vertices[6] = 0; _vertices[7] =  offset.x;          _vertices[8] =  offset.y;
  _vertices[9] = 0; _vertices[10] = offset.x + size.x; _vertices[11] = offset.y;
}

void Unit::setCurrentTexture(int texture) {
  for (int i = 0; i < 4; i++) {
    _layer[i] = (float)texture;
  }
}

void Unit::setHeightmapNormal(const glm::vec3& val) {
  for (int i = 0; i < 4; i++) {
    _heightmapNormal[3*i]     = val.x;
    _heightmapNormal[3*i + 1] = val.y;
    _heightmapNormal[3*i + 2] = val.z;
  }
}

int Unit::getNumSprites() const {
  return (int)_unitAsset->getSpriteInfo()[getCurrentTexture()].size();
}

int Unit::getNumTextures() const {
  return getTextureArray()->getCount();
}

#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

PYBIND11_MAKE_OPAQUE(std::vector<Unit*>)

void Unit::pythonBindings(py::module& m) {
  py::class_<Unit, std::shared_ptr<Unit>, ManagedElement>(m, "Unit")
    .def(py::init<std::shared_ptr<UnitManager>, std::shared_ptr<const UnitAsset>, glm::vec2>())
    .def_property_readonly("asset", &Unit::getUnitAsset)
    .def_property_readonly("screenRect", &Unit::getScreenRect)
    .def_property("currentSprite", &Unit::getCurrentSprite, &Unit::setCurrentSprite)
    .def_property("currentTexture", &Unit::getCurrentTexture, &Unit::setCurrentTexture)
    .def_property_readonly("numSprites", &Unit::getNumSprites)
    .def_property_readonly("numTextures", &Unit::getNumTextures)
    .def_property("position", &Unit::getPosition, &Unit::setPosition)
    .def_property("sizeFactor", &Unit::getSizeFactor, &Unit::setSizeFactor)
    .def_property("type", &Unit::getType, &Unit::setType)
    .def_property("lineOfSight", &Unit::getLineOfSight, &Unit::setLineOfSight)
    .def("getVisibleUnits", &Unit::getVisibleUnits)
    .def("getTargetPosition", &Unit::getTargetPosition)
    .def("setTarget", py::overload_cast<const glm::vec2&>(&Unit::setTarget))
    .def("setTarget", py::overload_cast<std::shared_ptr<Unit>>(&Unit::setTarget))
    .def("hasReachedTarget", &Unit::hasReachedTarget)
    .def("stopMoving", &Unit::stopMoving)
    .def_property("direction", &Unit::getDirection, &Unit::setDirection)
    .def_readwrite("stopOnReachTarget", &Unit::_stopOnReachTarget)
    .def_readwrite("targetAcceptanceRadius", &Unit::_targetAcceptanceRadius)
    .def_property("_orientation", &Unit::getOrientation, &Unit::setOrientation)
    .def_property("speed", &Unit::getSpeed, &Unit::setSpeed)
    .def_readonly("currentAnimationOrientation", &Unit::_currentAnimationOrientation)
    .def_readwrite("currentAnimFrame", &Unit::_currentAnimFrame)
    .def_readwrite("animPaused", &Unit::_animPaused)
    .def("isAnimationLoaded", &Unit::isAnimationLoaded)
    .def("startAnimation", py::overload_cast<int>(&Unit::startAnimation))
    .def("startAnimation", py::overload_cast<int, float>(&Unit::startAnimation))
    .def("startAnimation", py::overload_cast<int, const py::function&>(&Unit::startAnimation))
    .def("startAnimation", py::overload_cast<int, float, const py::function&>(&Unit::startAnimation))
    .def_readonly("onTargetOrDirectionSet", &Unit::_onTargetOrDirectionSet)
    .def_readonly("onStoppedMoving", &Unit::_onStoppedMoving)
    .def_readonly("onTeleported", &Unit::_onTeleported)

    // Properties that are used by the selector component (might need a refactor?)
    .def_readwrite("canBeSelected", &Unit::_canBeSelected)
    .def_readwrite("displayablePercentageValue", &Unit::_displayablePercentageValue)
    .def_readwrite("displayableValueColor", &Unit::_displayableValueColor)
    .def_readwrite("shouldDisplayGauge", &Unit::_shouldDisplayGauge)
    .def_readwrite("displayableText", &Unit::_displayableText);

  py::bind_vector<std::vector<Unit*>>(m, "UnitVector");
}