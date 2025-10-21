#include "Camera.h"

#include "Component.h"
#include "FrameBufferObject.h"
#include "Program.h"
#include "TexturedRectangle.h"
#include "utils.h"

#include <algorithm>

void Camera::apply(int msElapsed) {
  if (_lerpTimeMs > 0) {
    _currentPosition += (_targetPosition - _currentPosition) * (float)msElapsed / (float)_lerpTimeMs;
    _currentDirection += (_targetDirection - _currentDirection) * (float)msElapsed / (float)_lerpTimeMs;
    _currentUpVector += (_targetUpVector - _currentUpVector) * (float)msElapsed / (float)_lerpTimeMs;

    _lerpTimeMs = std::max(_lerpTimeMs - msElapsed, 0);
  }
  else {
    _currentPosition = _targetPosition;
    _currentDirection = _targetDirection;
    _currentUpVector = _targetUpVector;
  }

  _view = glm::lookAt(
    getCurrentPosition(),
    getCurrentPosition() + getCurrentDirection(),
    getCurrentUpVector()
  );

  _viewProjection = _projection * _view;
}

void Camera::renderComponents(const std::vector<std::shared_ptr<Component>>& components) const {
  SCOPE_BIND_PTR(_frameBufferObject)
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  for (auto& component : components) {
    component->render(this);
  }
}

glm::ivec2 Camera::getViewportSize() const {
  return _frameBufferObject->getSize();
}

void Camera::setViewportSize(const glm::ivec2& viewportSize) {
  if (!_frameBufferObject.get() || viewportSize != _frameBufferObject->getSize()) {
    _frameBufferObject = std::make_shared<FrameBufferObject>(viewportSize, GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE);
    _depthInColorBufferFBO = std::make_shared<FrameBufferObject>(getViewportSize(), GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE);
    _depthTexturedRectangle = std::make_shared<TexturedRectangle>(getDepthBuffer());
  }

  glViewport(0, 0, (GLint)viewportSize.x, (GLint)viewportSize.y);
  _aspectRatio = (float)viewportSize.x / (float)viewportSize.y;
  _projection = glm::perspective(glm::radians(_fovAngle), _aspectRatio, _nearPlane, _farPlane);

  apply(0);
}

void Camera::interpolateFrom(const Camera& otherCamera, int lerpTimeMs) {
  _currentPosition = otherCamera.getCurrentPosition();
  _currentDirection = otherCamera.getCurrentDirection();
  _currentUpVector = otherCamera.getCurrentUpVector();

  _lerpTimeMs = lerpTimeMs;
}

std::shared_ptr<const Texture> Camera::getColorBuffer() const {
  return _frameBufferObject->getColorBuffer();
}

std::shared_ptr<const Texture> Camera::getDepthBuffer() const {
  return _frameBufferObject->getDepthBuffer();
}

glm::vec2 Camera::screenToWorldPos(glm::ivec2 screenTarget) const {
  screenTarget.y = _depthInColorBufferFBO->getSize().y - screenTarget.y; // Inverted coordinates

  SCOPE_BIND_PTR(_depthInColorBufferFBO)
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  static const Program depthInColorBufferShader = Program("2D_shaders/2D.vert", "2D_shaders/depthToColor.frag");
  _depthTexturedRectangle->render(&depthInColorBufferShader);

  GLubyte depthBytes[4];
  glReadPixels(screenTarget.x, screenTarget.y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, &depthBytes[0]);

  const glm::vec4 bit_shift = glm::vec4(1.0 / (256.0 * 256.0 * 256.0), 1.0 / (256.0 * 256.0), 1.0 / 256.0, 1.0);
  float depth = glm::dot(glm::vec4(depthBytes[0], depthBytes[1], depthBytes[2], depthBytes[3]) / 255.f, bit_shift);

  glm::vec3 modelCoord = glm::unProject(glm::vec3(screenTarget.x, screenTarget.y, depth),
    glm::mat4(1.f), getViewProjectionMatrix(),
    glm::vec4(0, 0, _depthInColorBufferFBO->getSize().x, _depthInColorBufferFBO->getSize().y));

  return glm::vec2(modelCoord.x, modelCoord.y);
}

void Camera::pythonBindings(py::module& m) {
  py::class_<Camera, std::shared_ptr<Camera>>(m, "Camera")
    .def(py::init<>())
    .def(py::init<const Camera&>())
    .def_property("getViewportSize", &Camera::getViewportSize, &Camera::setViewportSize)
    .def_property("targetPosition", &Camera::getTargetPosition, &Camera::setTargetPosition)
    .def_property("targetDirection", &Camera::getTargetDirection, &Camera::setTargetDirection)
    .def_property("targetUpVector", &Camera::getTargetUpVector, &Camera::setTargetUpVector)
    .def_property_readonly("currentPosition", &Camera::getCurrentPosition)
    .def_property_readonly("currentDirection", &Camera::getCurrentDirection)
    .def_property_readonly("currentUpVector", &Camera::getCurrentUpVector)
    .def("interpolateFrom", &Camera::interpolateFrom)
    .def_readwrite("lerpTimeMs", &Camera::_lerpTimeMs)
    .def("screenToWorldPos", &Camera::screenToWorldPos);
}
