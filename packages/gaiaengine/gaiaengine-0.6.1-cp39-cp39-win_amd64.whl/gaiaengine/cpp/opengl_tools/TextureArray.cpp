#include "TextureArray.h"

#include "utils.h"

#include <cmath>
#include <sstream>

TextureArray::TextureArray(const std::vector<std::string>& texturePaths, int maxMipMaps):
  TextureArray(loadTextures(texturePaths), maxMipMaps)
{}

std::vector<std::shared_ptr<SDL_Surface>> TextureArray::loadTextures(const std::vector<std::string>& texturePaths) {
  std::vector<std::shared_ptr<SDL_Surface>> textures(texturePaths.size());

  for (int i = 0; i < texturePaths.size(); i++) {
    textures[i] = ut::loadImage(texturePaths[i]);
  }

  return textures;
}

TextureArray::TextureArray(const std::vector<std::shared_ptr<SDL_Surface>>& textures, int maxMipMaps):
  GLObject(),
  _count((int)textures.size())
{
  for (int i = 0; i < textures.size(); i++) {
    _texSizes.push_back(glm::vec2(textures[i]->w, textures[i]->h));

    if (_texSizes[i].x > _maxTexSize.x)
      _maxTexSize.x = _texSizes[i].x;
    if (_texSizes[i].y > _maxTexSize.y)
      _maxTexSize.y = _texSizes[i].y;
  }

  bind();

  // Max number of mip maps so that openGL doesn't throw an error
  maxMipMaps = std::min(maxMipMaps, ((int)std::log2(std::max(_maxTexSize.x, _maxTexSize.y)) + 1));
  glTexStorage3D(GL_TEXTURE_2D_ARRAY, maxMipMaps, GL_RGBA8, (GLsizei)_maxTexSize.x, (GLsizei)_maxTexSize.y, _count);

  for (int i = 0; i < _count; i++) {
    std::shared_ptr<SDL_Surface> texture = textures[i];

    // Incompatible image, converting to an OpenGL understandable format
    if (texture->format->format != SDL_PIXELFORMAT_ABGR8888) {
      texture = ut::SDL_make_shared(SDL_ConvertSurfaceFormat(texture.get(), SDL_PIXELFORMAT_ABGR8888, 0));
    }

    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, i,
      (GLsizei)_texSizes[i].x, (GLsizei)_texSizes[i].y, 1,
      GL_RGBA, GL_UNSIGNED_BYTE, texture->pixels
    );
  }

  glGenerateMipmap(GL_TEXTURE_2D_ARRAY);
  glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
  
  unbind();
}