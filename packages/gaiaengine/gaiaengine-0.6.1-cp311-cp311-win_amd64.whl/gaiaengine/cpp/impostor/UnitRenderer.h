#pragma once

#include "BasicGLObjects.h"
#include "Program.h"

#include <memory>
#include <vector>

class Camera;
class Unit;
class TextureArray;

class UnitRenderer {
public:
  UnitRenderer();

  inline float getUnitNearPlane() const { return _unitNearPlane; }
  void setUnitNearPlane(float val);

  glm::mat4 getModelMatrix(const Camera* camera) const;

  void loadUnits(const std::vector<std::shared_ptr<Unit>>& visibleUnits, bool onlyOnce = false);
  void render(const Camera* camera) const;

private:
  void fillBufferData(GLenum renderType);
  void processSpree(const std::vector<std::shared_ptr<Unit>>& visibleUnits, int currentSpreeLength, int firstIndexSpree);
  int renderPass() const;

  int _capacity = 0;
  bool _fixedCapacity = false;
  float _unitNearPlane = -1.f;

  std::vector<float> _data;

  Program _unitShader = Program("unit.vert", "unit.frag");
  VertexArrayObject _vao;
  VertexBufferObject _vbo;
  IndexBufferObject _ibo;
  std::vector<const TextureArray*> _textures;
  std::vector<int> _nbUnitsInSpree;
};
