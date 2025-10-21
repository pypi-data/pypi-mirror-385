#pragma once

#include <opengl.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include "utils.h"

#include <memory>
#include <vector>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Component;
class FrameBufferObject;
class Texture;
class TexturedRectangle;

class Camera {
public:
  Camera() = default;

  virtual void apply(int msElapsed);

  void renderComponents(const std::vector<std::shared_ptr<Component>>& components) const;

  glm::ivec2 getViewportSize() const;
  void setViewportSize(const glm::ivec2& viewportSize);

  inline glm::vec3 getTargetPosition() const {return _targetPosition;}
  inline void setTargetPosition(const glm::vec3& val) { _targetPosition = val; }

  inline glm::vec3 getTargetDirection() const { return _targetDirection; }
  inline void setTargetDirection(glm::vec3 val) { _targetDirection = glm::normalize(val); }

  inline glm::vec3 getTargetUpVector() const { return _targetUpVector; }
  inline void setTargetUpVector(glm::vec3 val) { _targetUpVector = val; }

  inline glm::vec3 getCurrentPosition() const { return _currentPosition; }
  inline glm::vec3 getCurrentDirection() const { return _currentDirection; }
  inline glm::vec3 getCurrentUpVector() const { return _currentUpVector; }

  void interpolateFrom(const Camera& otherCamera, int lerpTimeMs);

  inline float getFovAngle() const {return _fovAngle;}
  inline float getRatio() const {return _aspectRatio;}
  inline glm::mat4 getProjectionMatrix() const { return _projection; }
  inline glm::mat4 getViewMatrix() const { return _view; }
  inline glm::mat4 getViewProjectionMatrix() const {return _viewProjection;}

  std::shared_ptr<const Texture> getColorBuffer() const;
  std::shared_ptr<const Texture> getDepthBuffer() const;

  glm::vec2 screenToWorldPos(glm::ivec2 screenTarget) const;

  static void pythonBindings(py::module& m);

protected:
  glm::mat4 _projection = glm::mat4(1.f);
  glm::mat4 _view = glm::mat4(1.f);
  glm::mat4 _viewProjection = glm::mat4(1.f);

private:
  std::shared_ptr<FrameBufferObject> _frameBufferObject;

  float _fovAngle = 45.f;
  float _aspectRatio = 1.f;
  float _nearPlane = 1.f;
  float _farPlane = 1000.f;

  glm::vec3 _targetPosition = glm::vec3(0.f);
  glm::vec3 _targetDirection = glm::vec3(1.f, 0.f, 0.f);
  glm::vec3 _targetUpVector = glm::vec3(0.f, 0.f, 1.f);
  glm::vec3 _currentPosition = glm::vec3(0.f);
  glm::vec3 _currentDirection = glm::vec3(1.f, 0.f, 0.f);
  glm::vec3 _currentUpVector = glm::vec3(0.f, 0.f, 1.f);

  int _lerpTimeMs = 0;

  std::shared_ptr<FrameBufferObject> _depthInColorBufferFBO;
  std::shared_ptr<TexturedRectangle> _depthTexturedRectangle;
};
