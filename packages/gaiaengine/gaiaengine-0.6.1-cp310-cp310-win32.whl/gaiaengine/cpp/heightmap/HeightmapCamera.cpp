#include "HeightmapCamera.h"

#include "EventManager.h"
#include "Heightmap.h"
#include "Unit.h"
#include "Window.h"

#include <algorithm>

HeightmapCamera::HeightmapCamera(const std::shared_ptr<Heightmap>& heightmap) :
  Camera(),
  _heightmap(heightmap)
{
  if (heightmap.get() == nullptr)
    throw std::invalid_argument("Invalid Heightmap object");

  _aim2DPosition = glm::vec2(heightmap->getNbCells()) / 2.f;
}

void HeightmapCamera::apply(int msElapsed) {
  if (std::shared_ptr<Unit> strongUnit = getLockedOnUnit())
    setAim2DPosition(strongUnit->getPosition());

  if (_followTerrainHeight)
    _heightAtAim = _heightmap->getHeight(getAim2DPosition());

  setTargetPosition(getAimPosition() + ut::carthesian(getRadius(), getTheta(), getPhi()));
  setTargetDirection(getAimPosition() - getTargetPosition());
  setTargetUpVector(ut::carthesian(1.f, getTheta(), getPhi() + getFovAngle() / 2.f - 90.f));

  Camera::apply(msElapsed);
}

void HeightmapCamera::translateInCameraCoordinates(float dx, float dy) {
  setAim2DPosition(_aim2DPosition + glm::vec2(
    dx * cos(glm::radians(getTheta() + 90.f)) + dy * sin(glm::radians(getTheta() + 90.f)),
    dx * sin(glm::radians(getTheta() + 90.f)) - dy * cos(glm::radians(getTheta() + 90.f))
  ));
}

void HeightmapCamera::setAim2DPosition(glm::vec2 val) {
  _aim2DPosition = val;

  glm::vec2 maxCoordinates = _heightmap->getMaxCoordinates();
  _aim2DPosition.x = std::clamp(_aim2DPosition.x, 0.f, maxCoordinates.x);
  _aim2DPosition.y = std::clamp(_aim2DPosition.y, 0.f, maxCoordinates.y);
}

void HeightmapCamera::pythonBindings(py::module& m) {
  py::class_<HeightmapCamera, std::shared_ptr<HeightmapCamera>, Camera>(m, "HeightmapCamera")
    .def(py::init<const HeightmapCamera&>())
    .def(py::init<const std::shared_ptr<Heightmap>&>())
  .def("translateInCameraCoordinates", &HeightmapCamera::translateInCameraCoordinates)
  .def_property("lockedOnUnit", &HeightmapCamera::getLockedOnUnit, &HeightmapCamera::setLockedOnUnit)
  .def_property("aim2DPosition", &HeightmapCamera::getAim2DPosition, &HeightmapCamera::setAim2DPosition)
  .def_readwrite("additionalHeight", &HeightmapCamera::_additionalHeight)
  .def_readwrite("followTerrainHeight", &HeightmapCamera::_followTerrainHeight)
  .def_property("radius", &HeightmapCamera::getRadius, &HeightmapCamera::setRadius)
  .def_property("theta", &HeightmapCamera::getTheta, &HeightmapCamera::setTheta)
  .def_property("phi", &HeightmapCamera::getPhi, &HeightmapCamera::setPhi);
}