#pragma once

#include <glm/glm.hpp>


#include "GLObject.h"

#include <memory>
#include <string>
#include <vector>

struct SDL_Surface;

class TextureArray : public GLObject<TextureArray> {
public:
  TextureArray(const std::vector<std::string>& texturePaths, int maxMipMaps = 4);
  TextureArray(const std::vector<std::shared_ptr<SDL_Surface>>& imageData, int maxMipMaps = 4);

  // Returns the size of the current texture relative to the size of the array texture
  inline glm::vec4 getTexRectangle(int index) const {
    return glm::vec4(0,
                     0,
                     (float) _texSizes[index].x / (float) _maxTexSize.x,
                     (float) _texSizes[index].y / (float) _maxTexSize.y);
  }


  inline int getCount() const { return _count; }
  inline const glm::ivec2& getMaxTexSize() const { return _maxTexSize; }
  inline const glm::ivec2& getTexSize(int index) const { return _texSizes[index]; }

private:
  static void genObject(GLuint& objectID) { glGenTextures(1, &objectID); };
  static void bindObject(GLuint objectID) { glBindTexture(GL_TEXTURE_2D_ARRAY, objectID); };
  static void deleteObject(GLuint objectID) { glDeleteTextures(1, &objectID); };

  friend class GLObject;

  std::vector<std::shared_ptr<SDL_Surface>> loadTextures(const std::vector<std::string>& texturePaths);

  int _count = 0;

  glm::ivec2 _maxTexSize = glm::ivec2(0);
  std::vector<glm::ivec2> _texSizes;
};
