#pragma once

#include <glm/glm.hpp>
#include <SDL.h>

#include "Color.h"

#include <cstdlib>
#include <memory>
#include <sstream>
#include <string>

#include <pybind11/pybind11.h>

namespace py = pybind11;

#define GAIA_SOURCE_PATH std::string(std::getenv("GAIA_SOURCE_PATH"))

// ut = utils
namespace ut {
#ifdef _WIN32
  const std::string os_pathsep(";");
#else
  const std::string os_pathsep(":");
#endif

  glm::vec3 carthesian(float r, float theta, float phi);
  glm::vec3 spherical(float x, float y, float z);

  inline glm::vec3 carthesian(glm::vec3 u) {return carthesian(u.x,u.y,u.z);}
  inline glm::vec3 spherical (glm::vec3 u) {return spherical (u.x,u.y,u.z);}

  // Convert from a rectangle where (x,y) = corner and (z,w) = (width, height)
  // to a rectangle where x = left, y = top, z = right, w = bottom
  void convertToAbsoluteRectangle(glm::ivec4& rect);
  
  bool getRectanglesIntersect(glm::ivec4 a, glm::ivec4 b);

  float getRectangleCircleDistance(glm::ivec4 rect, const glm::vec2& circleCenter);

  std::string textFileToString(const std::string& path);

  inline bool endsWith(std::string const& value, std::string const& ending)
  {
    if (ending.size() > value.size()) return false;
    return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
  }

  template <typename T>
  std::string to_string_with_precision(const T a_value, const int n) {
    std::ostringstream out;
    out.precision(n);
    out << std::fixed << a_value;
    return std::move(out).str();
  }

  inline std::shared_ptr<SDL_Palette> SDL_make_shared(SDL_Palette* palette) {
    return std::shared_ptr<SDL_Palette>(palette, [](SDL_Palette* palette) { SDL_FreePalette(palette); });
  }

  inline std::shared_ptr<SDL_Surface> SDL_make_shared(SDL_Surface* surface) {
    return std::shared_ptr<SDL_Surface>(surface, [](SDL_Surface* surface) { SDL_FreeSurface(surface); });
  }

  // Loads a JASC Palette (PAL) file
  std::shared_ptr<SDL_Palette> loadPalette(const std::string& filePath);
  std::shared_ptr<SDL_Surface> createSurface(const glm::ivec2& size);
  std::shared_ptr<SDL_Surface> createColoredSurface(const glm::ivec2& size, const Color& color);
  std::shared_ptr<SDL_Surface> loadImage(const std::string& filePath);

  void setPixelInSurface(std::shared_ptr<SDL_Surface> surface, int x, int y, const SDL_Color& value);
  void setPixelInSurface(std::shared_ptr<SDL_Surface> surface, int x, int y, Uint32 value);

  // Taken from https://github.com/pybind/pybind11/issues/1622
  class PyOutStreamsRedirectToStringScoped {
    py::object _stdout;
    py::object _stderr;
    py::object _stdout_buffer;
    py::object _stderr_buffer;
  public:
    PyOutStreamsRedirectToStringScoped() {
      auto sysm = py::module::import("sys");
      _stdout = sysm.attr("stdout");
      _stderr = sysm.attr("stderr");
      auto stringio = py::module::import("io").attr("StringIO");
      _stdout_buffer = stringio();  // Other filelike object can be used here as well, such as objects created by pybind11
      _stderr_buffer = stringio();
      sysm.attr("stdout") = _stdout_buffer;
      sysm.attr("stderr") = _stderr_buffer;
    }

    PyOutStreamsRedirectToStringScoped(const PyOutStreamsRedirectToStringScoped &) = delete;
    PyOutStreamsRedirectToStringScoped(PyOutStreamsRedirectToStringScoped &&other) = delete;
    PyOutStreamsRedirectToStringScoped &operator=(const PyOutStreamsRedirectToStringScoped &) = delete;
    PyOutStreamsRedirectToStringScoped &operator=(PyOutStreamsRedirectToStringScoped &&) = delete;

    ~PyOutStreamsRedirectToStringScoped() {
      auto sysm = py::module::import("sys");
      sysm.attr("stdout") = _stdout;
      sysm.attr("stderr") = _stderr;
    }

    std::string stdoutString() {
      _stdout_buffer.attr("seek")(0);
      return py::str(_stdout_buffer.attr("read")());
    }
    std::string stderrString() {
      _stderr_buffer.attr("seek")(0);
      return py::str(_stderr_buffer.attr("read")());
    }
  };

  // Redirecting the output of the python print function to a string
  template <typename... Args>
  std::string pyPrintToString(Args &&...args) {
    PyOutStreamsRedirectToStringScoped redirectHelper;
    py::print(args...);
    return redirectHelper.stdoutString();
  }
}

bool glCheckError(const char *file, int line);

// regex to replace gl calls: ([_a-zA-Z]* = )?(\bgl[^ :;>]*\([^;]*\));
// replace with GL_CHECK($2)
#define GL_CHECK(expr) {expr; glCheckError(__FILE__,__LINE__);}
