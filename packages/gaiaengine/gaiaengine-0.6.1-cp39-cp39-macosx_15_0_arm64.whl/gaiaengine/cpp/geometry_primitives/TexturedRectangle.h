#pragma once

#include <glm/glm.hpp>

#include "BasicGLObjects.h"

#include <array>
#include <memory>

class Program;
class Texture;

class TexturedRectangle {
public:
  TexturedRectangle (std::shared_ptr<const Texture> texture, const glm::vec4& glRect = glm::vec4(-1,-1,2,2));

  void render(const Program* shader = nullptr) const;

private:  
  std::array<float, 16> _verticesAndCoord{};

  std::shared_ptr<const Texture> _texture;
  VertexArrayObject _vao;
  VertexBufferObject _vbo;
};
