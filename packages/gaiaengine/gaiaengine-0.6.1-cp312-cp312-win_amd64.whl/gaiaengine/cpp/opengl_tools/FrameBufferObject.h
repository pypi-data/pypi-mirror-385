#pragma once

#include <glm/glm.hpp>

#include "GLObject.h"

#include <memory>

class Texture;

class FrameBufferObject : public GLObject<FrameBufferObject> {
public:
  FrameBufferObject(const glm::ivec2& size, GLenum colorBufferInternalFormat, GLenum colorBufferFormat, GLenum colorBufferType);

  inline std::shared_ptr<const Texture> getColorBuffer() const {return _colorBuffer;}
  inline std::shared_ptr<const Texture> getDepthBuffer() const {return _depthBuffer;}

  inline glm::ivec2 getSize() const { return _size; }

private:
  static void genObject(GLuint& objectID) { glGenFramebuffers(1, &objectID); };
  static void bindObject(GLuint objectID) { glBindFramebuffer(GL_FRAMEBUFFER, objectID); };
  static void deleteObject(GLuint objectID) { glDeleteFramebuffers(1, &objectID); };

  friend class GLObject;

  glm::ivec2 _size = glm::ivec2(0);
  std::shared_ptr<Texture> _colorBuffer;
  std::shared_ptr<Texture> _depthBuffer;
};
