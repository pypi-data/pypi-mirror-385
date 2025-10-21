#include "ColoredRectangles.h"

#include "Program.h"

ColoredRectangles::ColoredRectangles (glm::vec4 color, bool filled):
  _color(color),
  _filled(filled)
{
  SCOPE_BIND(_vao)
  SCOPE_BIND(_vbo)

  glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(0));

  glEnableVertexAttribArray(0);
}

ColoredRectangles::ColoredRectangles (glm::vec4 color, const glm::ivec4& rectangle, const glm::ivec2& windowSize, bool filled):
 ColoredRectangles(color, std::vector<glm::ivec4>(1,rectangle), windowSize, filled)
{}

ColoredRectangles::ColoredRectangles (glm::vec4 color, const std::vector<glm::ivec4>& rectangles, const glm::ivec2& windowSize, bool filled):
  ColoredRectangles(color, filled)
{
  setRectangles(rectangles, windowSize);
}

void ColoredRectangles::setRectangles(const glm::ivec4& rectangle, const glm::ivec2& windowSize) {
  setRectangles(std::vector<glm::ivec4>(1,rectangle), windowSize);
}

void ColoredRectangles::setRectangles(const std::vector<glm::ivec4>& rectangles, const glm::ivec2& windowSize) {
  SCOPE_BIND(_vbo)
  _nbRect = (GLsizei) rectangles.size();
  size_t rectGLDataSize;

  if (_nbRect == 0)
    return;

  if (_filled)
    rectGLDataSize = 12;
  else
    rectGLDataSize = 16;

  std::vector<float> bufferData(rectGLDataSize * _nbRect);

  for (int i = 0; i < _nbRect; i++) {
    glm::vec4 glRectangle = windowRectCoordsToGLRectCoords(rectangles[i], windowSize);
    float x0 = glRectangle.x;
    float y0 = glRectangle.y;
    float x1 = glRectangle.x + glRectangle.z;
    float y1 = glRectangle.y + glRectangle.w;

    if (_filled) {
      struct {float x, y;} data[6] = {
        { x0, y0 }, { x1, y1 }, { x0, y1 },
        { x0, y0 }, { x1, y0 }, { x1, y1 }
      };
      VertexBufferObject::cpuBufferSubData(bufferData, i * rectGLDataSize , rectGLDataSize, data);
    }
    else {
      x0 += _linesOffset; y0 += _linesOffset; x1 -= 2*_linesOffset; y1 -= 2*_linesOffset;

      struct {float x, y;} data[8] = {
        { x0, y0 }, { x0, y1 }, { x0, y1 }, { x1, y1 },
        { x1, y1 }, { x1, y0 }, { x1, y0 }, { x0, y0 }
      };
      VertexBufferObject::cpuBufferSubData(bufferData, i * rectGLDataSize , rectGLDataSize, data);
    }

  }

  glBufferData(GL_ARRAY_BUFFER, bufferData.size() * sizeof(float), &bufferData[0], GL_DYNAMIC_DRAW);
}

glm::vec4 ColoredRectangles::windowRectCoordsToGLRectCoords(const glm::ivec4& windowRect, const glm::ivec2& windowSize) {
  return glm::vec4(2 * windowRect.x / (float)windowSize.x - 1,
    1 - 2 * (windowRect.y + windowRect.w) / (float)windowSize.y,
    2 * windowRect.z / (float)windowSize.x,
    2 * windowRect.w / (float)windowSize.y);
}

void ColoredRectangles::render() const {
  SCOPE_BIND(_vao)

  glEnable (GL_BLEND);
  glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  static const Program plainColorShader = Program("2D_shaders/2D_noTexCoords.vert", "2D_shaders/plainColor.frag");

  SCOPE_BIND(plainColorShader)
  glUniform4fv(plainColorShader.getUniformLocation("color"), 1, &_color[0]);

  if (_filled)
    glDrawArrays(GL_TRIANGLES, 0, 6*_nbRect);
  else
    glDrawArrays(GL_LINES, 0, 8*_nbRect);

  glDisable(GL_BLEND);
}
