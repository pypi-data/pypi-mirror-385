#pragma once

#include <glm/glm.hpp>


#include "Color.h"
#include "GLObject.h"

#include <string>


class Texture : public GLObject<Texture> {
public:
  Texture();
  Texture(const std::string& filePath);

  void loadFromFile(const std::string& filePath);

  inline bool isEmpty() const {return _size == glm::uvec2(0,0);}
  inline glm::uvec2 getSize() const {return _size;}

  inline void attachToBoundFBO(GLenum attachment) const {
    glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, getObjectID(), 0);
  }

  inline std::string getFilePath() const { return _filePath; }

  static void pythonBindings(py::module& m);

private:
  static void genObject(GLuint& objectID) { glGenTextures(1, &objectID); };
  static void bindObject(GLuint objectID) { glBindTexture(GL_TEXTURE_2D, objectID); };
  static void deleteObject(GLuint objectID) { glDeleteTextures(1, &objectID); };

  friend class GLObject;

  glm::uvec2 _size = glm::uvec2(0);
  std::string _filePath;
};
