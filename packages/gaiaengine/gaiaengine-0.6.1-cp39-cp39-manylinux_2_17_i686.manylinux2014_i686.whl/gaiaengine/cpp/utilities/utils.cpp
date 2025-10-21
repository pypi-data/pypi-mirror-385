#include "utils.h"

#include <opengl.h>
#include <SDL_image.h>
#include <SDL_log.h>

#include <algorithm>
#include <fstream>
#include <stdexcept>
#include <sstream>

glm::vec3 ut::carthesian(float r, float theta, float phi) {
  glm::vec3 u;

  u.x = r * sin(glm::radians(phi)) * cos(glm::radians(theta));
  u.y = r * sin(glm::radians(phi)) * sin(glm::radians(theta));
  u.z = r * cos(glm::radians(phi));

  return u;
}

glm::vec3 ut::spherical(float x, float y, float z) {
  glm::vec3 u(0,0,0);
  u.x = sqrt(x*x + y*y + z*z);
  if (u.x != 0) {
    u.y = glm::degrees(atan2(y,x));
    if (u.y < 0)
      u.y += 360;

    u.z = glm::degrees(acos(z/u.x));
  }

  return u;
}

void ut::convertToAbsoluteRectangle(glm::ivec4& rect) {
  rect.z += rect.x;
  rect.w += rect.y;

  if (rect.z < rect.x)
    std::swap(rect.z, rect.x);
  if (rect.w < rect.y)
    std::swap(rect.w, rect.y);
}

bool ut::getRectanglesIntersect(glm::ivec4 a, glm::ivec4 b) {
  convertToAbsoluteRectangle(a);
  convertToAbsoluteRectangle(b);
  
  return  a.x < b.z && a.z > b.x && a.y < b.w && a.w > b.y;
}

float ut::getRectangleCircleDistance(glm::ivec4 rect, const glm::vec2& circleCenter) {
  convertToAbsoluteRectangle(rect);

  float closestX = std::clamp(circleCenter.x, (float)rect.x, (float)rect.z);
  float closestY = std::clamp(circleCenter.y, (float)rect.y, (float)rect.w);

  float dx = circleCenter.x - closestX;
  float dy = circleCenter.y - closestY;

  return sqrt(dx * dx + dy * dy);
}

std::string ut::textFileToString(const std::string& path) {
  SDL_RWops* ops = SDL_RWFromFile(path.c_str(), "rb");

  if (ops == nullptr)
    throw std::runtime_error(SDL_GetError());

  Sint64 res_size = SDL_RWsize(ops);
  char* tmpChar = new char[res_size + 1];

  Sint64 nb_read_total = 0, nb_read = 1;
  char* buf = tmpChar;
  while (nb_read_total < res_size && nb_read != 0) {
    nb_read = SDL_RWread(ops, buf, 1, (res_size - nb_read_total));
    nb_read_total += nb_read;
    buf += nb_read;
  }

  if (nb_read_total != res_size) {
    delete[] tmpChar;
    return std::string();
  }

  tmpChar[nb_read_total] = '\0';
  std::string res(tmpChar);
  delete[] tmpChar;

  SDL_RWclose(ops);

  return res;
}

std::shared_ptr<SDL_Palette> ut::loadPalette(const std::string& filePath) {
  std::ifstream paletteFile(filePath);

  std::string line;
  std::getline(paletteFile, line); //'JASC-PAL'
  std::getline(paletteFile, line); //'0100'
  std::getline(paletteFile, line); // Number of colors

  std::shared_ptr<SDL_Palette> palette = ut::SDL_make_shared(SDL_AllocPalette(std::stoi(line)));

  for (int i = 0; i < palette->ncolors; i++) {
    std::getline(paletteFile, line);
    std::istringstream iss(line);
    
    // Need to use int variables, otherwise SDL_Color components are read as chars instead of bytes
    int r, g, b;
    iss >> r >> g >> b;
    SDL_Color currentColor;
    currentColor.r = (Uint8)r;
    currentColor.g = (Uint8)g;
    currentColor.b = (Uint8)b;
    currentColor.a = 255;
    palette->colors[i] = currentColor;
  }

  return palette;
}

std::shared_ptr<SDL_Surface> ut::createSurface(const glm::ivec2& size) {
  // Code example from https://wiki.libsdl.org/SDL_CreateRGBSurface

  /* Create a 32-bit surface with the bytes of each pixel in R,G,B,A order,
    as expected by OpenGL for textures */
  SDL_Surface* surface;

  Uint32 rmask, gmask, bmask, amask;

  /* SDL interprets each pixel as a 32-bit number, so our masks must depend
   on the endianness (byte order) of the machine */
#if SDL_BYTEORDER == SDL_BIG_ENDIAN
  rmask = 0xff000000;
  gmask = 0x00ff0000;
  bmask = 0x0000ff00;
  amask = 0x000000ff;
#else
  rmask = 0x000000ff;
  gmask = 0x0000ff00;
  bmask = 0x00ff0000;
  amask = 0xff000000;
#endif

  surface = SDL_CreateRGBSurface(0, size.x, size.y, 32, rmask, gmask, bmask, amask);

  return SDL_make_shared(surface);
}

std::shared_ptr<SDL_Surface> ut::createColoredSurface(const glm::ivec2& size, const Color& color) {
  std::shared_ptr<SDL_Surface> surface = createSurface(size);
  SDL_FillRect(surface.get(), nullptr, SDL_MapRGBA(surface->format, color.r, color.g, color.b, color.a));
  return surface;
}

std::shared_ptr<SDL_Surface> ut::loadImage(const std::string& filePath) {
  SDL_Surface* surface = IMG_Load(filePath.c_str());
  if (!surface)
    throw std::runtime_error(IMG_GetError());

  return SDL_make_shared(surface);
}

void ut::setPixelInSurface(std::shared_ptr<SDL_Surface> surface, int x, int y, Uint32 value) {
  if (x >= surface->w || y >= surface->h) {
    SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Trying to set a pixel outside of the surface");
    return;
  }

  // Using ptrdiff_t to avoid an overflow warning
  Uint32* const target_pixel = reinterpret_cast<Uint32*>(static_cast<Uint8*>(surface->pixels)
    + y * std::ptrdiff_t(surface->pitch)
    + x * std::ptrdiff_t(surface->format->BytesPerPixel));
  
  *target_pixel = value;
}

void ut::setPixelInSurface(std::shared_ptr<SDL_Surface> surface, int x, int y, const SDL_Color& value) {
  setPixelInSurface(surface, x, y, SDL_MapRGBA(surface->format, value.r, value.g, value.b, value.a));
}

bool glCheckError(const char *file, int line) {
  GLenum err (glGetError());

  bool isError = false;

  while(err != GL_NO_ERROR) {
    std::string error;

    switch(err) {
      case GL_INVALID_OPERATION:             error="INVALID_OPERATION";      break;
      case GL_INVALID_ENUM:                  error="INVALID_ENUM";           break;
      case GL_INVALID_VALUE:                 error="INVALID_VALUE";          break;
      case GL_OUT_OF_MEMORY:                 error="OUT_OF_MEMORY";          break;
      case GL_INVALID_FRAMEBUFFER_OPERATION: error="INVALID_FRAMEBUFFER_OPERATION";  break;
#ifndef __APPLE__
      case GL_STACK_UNDERFLOW:               error="STACK_UNDERFLOW";        break;
      case GL_STACK_OVERFLOW:                error="STACK_OVERFLOW";         break;
#endif
    }

    SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "GL_%s - %s: %d", error.c_str(), file, line);
    err = glGetError();
    isError = true;
  }

  return isError;
}
