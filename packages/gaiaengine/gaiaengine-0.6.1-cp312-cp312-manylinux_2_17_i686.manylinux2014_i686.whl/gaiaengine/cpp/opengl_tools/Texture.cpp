#include "Texture.h"

#include <SDL_log.h>

#include "utils.h"

Texture::Texture():
  GLObject()
{}

Texture::Texture(const std::string& filePath):
  Texture()
{
  _filePath = filePath;
  loadFromFile(filePath);
}

void Texture::loadFromFile(const std::string& filePath) {
  std::shared_ptr<SDL_Surface> img = ut::loadImage(filePath);

  // Will be same as internalFormat
  GLenum format(0);

  if (img->format->BytesPerPixel == 3)
    format = GL_RGB;

  else if (img->format->BytesPerPixel == 4)
    format = GL_RGBA;

  else
    throw std::invalid_argument("Error in Texture::loadFromFile: format is not true color");

  // Opengl ES does not handle GL_BGR images
  if (img->format->Rmask != 0xff)
    throw std::invalid_argument("Error in Texture::loadFromFile: format not handled");

  _size.x = img->w;
  _size.y = img->h;

  bind();

  glTexImage2D(GL_TEXTURE_2D, 0, format, _size.x, _size.y, 0, format, GL_UNSIGNED_BYTE, img->pixels);

  glGenerateMipmap(GL_TEXTURE_2D);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);

  unbind();
}

void Texture::pythonBindings(py::module& m) {
  py::class_<Texture, std::shared_ptr<Texture>>(m, "Texture")
    .def(py::init<>())
    .def(py::init<const std::string&>())
    .def_property_readonly("filePath", &Texture::getFilePath);
}
