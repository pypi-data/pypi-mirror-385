#pragma once

#include <glm/glm.hpp>

#include "BasicGLObjects.h"

#include <memory>
#include <vector>

class ColoredRectangles {
public:
  ColoredRectangles (glm::vec4 color, bool filled = true);
  ColoredRectangles (glm::vec4 color, const glm::ivec4& rectangle, const glm::ivec2& windowSize, bool filled = true);
  ColoredRectangles (glm::vec4 color, const std::vector<glm::ivec4>& rectangles, const glm::ivec2& windowSize, bool filled = true);

  void render() const;

  void setRectangles(const glm::ivec4& rectangle, const glm::ivec2& windowSize);
  void setRectangles(const std::vector<glm::ivec4>& rectangles, const glm::ivec2& windowSize);

private:  
  glm::vec4 windowRectCoordsToGLRectCoords(const glm::ivec4& windowRect, const glm::ivec2& windowSize);

  // To avoid rounding to the left for the lines
  const float _linesOffset = 1e-5f;

  std::vector<float> _vertices;
  glm::vec4 _color = glm::vec4(0);
  bool _filled = false;

  GLsizei _nbRect = 0;

  VertexArrayObject _vao;
  VertexBufferObject _vbo;
};
