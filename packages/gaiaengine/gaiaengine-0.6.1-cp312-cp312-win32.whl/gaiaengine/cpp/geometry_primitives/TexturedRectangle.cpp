#include "TexturedRectangle.h"

#include "Program.h"
#include "Texture.h"

TexturedRectangle::TexturedRectangle(std::shared_ptr<const Texture> texture, const glm::vec4& glRect) :
  _texture(texture)
{
  _verticesAndCoord  = {
     glRect.x,            glRect.y,            0, 0,
     glRect.x + glRect.z, glRect.y,            1, 0,
     glRect.x,            glRect.y + glRect.w, 0, 1,
     glRect.x + glRect.z, glRect.y + glRect.w, 1, 1
  };

  SCOPE_BIND(_vao)
  SCOPE_BIND(_vbo)

  glBufferData(	GL_ARRAY_BUFFER, sizeof(_verticesAndCoord), &_verticesAndCoord[0], GL_STATIC_DRAW);

  glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(0));

  glEnableVertexAttribArray(0);
}

void TexturedRectangle::render(const Program* shader) const {
  static const Program defaultShader = Program("2D_shaders/2D.vert", "2D_shaders/simpleTexture.frag");

  if (shader == nullptr)
    shader = &defaultShader;

  SCOPE_BIND_PTR(shader)
  SCOPE_BIND(_vao)
  SCOPE_BIND_PTR(_texture)

  glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
}

