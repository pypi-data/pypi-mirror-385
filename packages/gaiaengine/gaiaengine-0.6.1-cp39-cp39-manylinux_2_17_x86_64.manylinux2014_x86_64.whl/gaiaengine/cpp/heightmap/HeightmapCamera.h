#pragma once

#include "Camera.h"

#include <algorithm>
#include <memory>

class Heightmap;
class Unit;


class HeightmapCamera : public Camera {
public:
  HeightmapCamera(const std::shared_ptr<Heightmap>& heightmap);

  void apply(int msElapsed) override;

  void translateInCameraCoordinates(float dx, float dy);

  inline glm::vec3 getPolarCoordinates() const { return glm::vec3(getRadius(), getTheta(), getPhi()); }
  inline void setPolarCoordinates(float r, float theta, float phi) { setRadius(r); setTheta(theta); setPhi(phi); }

  inline glm::vec3 getAimPosition() const { return glm::vec3(_aim2DPosition, _heightAtAim + _additionalHeight); }

  inline glm::vec2 getAim2DPosition() const { return _aim2DPosition; }
  void setAim2DPosition(glm::vec2 val);

  inline float getRadius() const { return _radius; }
  void setRadius(float val) { _radius = val; }

  inline float getTheta() const { return _theta; }
  inline void setTheta(float val) { _theta = val; }

  inline float getPhi() const { return _phi; }
  inline void setPhi(float val) { _phi = val; }

  inline std::shared_ptr<Unit> getLockedOnUnit() const { return _lockedOnUnit.lock(); }
  inline void setLockedOnUnit(std::shared_ptr<Unit> val) { _lockedOnUnit = val; }

  static void pythonBindings(py::module& m);
private:
  glm::vec2 _aim2DPosition = glm::vec2(0);
  float _heightAtAim = 0.f;
  bool _followTerrainHeight = false;
  // The camera points towards the center of a sphere located at 'aim'.
  // r, theta, phi follow the mathematical convention: theta is the azimuthal and phi the polar angle
  float _radius = 15.f;
  float _theta = -90.f;
  float _phi = 60.f;

  float _additionalHeight = 0.f; // Height added to the camera when clipping with the terrain

  std::shared_ptr<Heightmap> _heightmap;
  std::weak_ptr<Unit> _lockedOnUnit;
};
