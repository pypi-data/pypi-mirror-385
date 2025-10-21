// This files contains RAII classes that handle the lifetime of basic OpenGL objects:
// Index Buffer Objects (IBO)
// Vertex Array Objects (VAO)
// Vertex Buffer Objects (VBO)

#pragma once

#include "GLObject.h"

#include <cstddef>
#include <vector>

class VertexArrayObject : public GLObject<VertexArrayObject> {
public:
  VertexArrayObject() = default;
  
private:
  static void genObject(GLuint& objectID) { glGenVertexArrays(1, &objectID); };
  static void bindObject(GLuint objectID) { glBindVertexArray(objectID); };
  static void deleteObject(GLuint objectID) { glDeleteVertexArrays(1, &objectID); };

  friend class GLObject;
};

class VertexBufferObject : public GLObject<VertexBufferObject> {
public:
  VertexBufferObject() = default;

  // Mimics glBufferSubData on the CPU as OpenGL ES drivers sometimes send the whole buffer each time
  static void cpuBufferSubData(std::vector<float>& bufferData, size_t offset, size_t size, const void* data);

private:
  static void genObject(GLuint& objectID) { glGenBuffers(1, &objectID); };
  static void bindObject(GLuint objectID) { glBindBuffer(GL_ARRAY_BUFFER, objectID); };
  static void deleteObject(GLuint objectID) { glDeleteBuffers(1, &objectID); };

  friend class GLObject;
};

class IndexBufferObject : public GLObject<IndexBufferObject> {
public:
  IndexBufferObject() = default;

private:
  static void genObject(GLuint& objectID) { glGenBuffers(1, &objectID); };
  static void bindObject(GLuint objectID) { glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, objectID); };
  static void deleteObject(GLuint objectID) { glDeleteBuffers(1, &objectID); };

  friend class GLObject;
};
