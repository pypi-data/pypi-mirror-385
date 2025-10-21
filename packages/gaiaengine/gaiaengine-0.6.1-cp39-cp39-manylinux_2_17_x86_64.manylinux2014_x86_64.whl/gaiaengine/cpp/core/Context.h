#pragma once

#include <glm/glm.hpp>
#include <SDL.h>

#include <pybind11/pybind11.h>

namespace py = pybind11;

// Handles the life time of SDL
class Context {
public:
  Context();
  ~Context();

  Context(Context const&) = delete;
  void operator=(Context const&) = delete;

  static bool wasSDLInitialized();
  static bool isGLContextValid();

  static void setWindow(SDL_Window* window);
  static SDL_GLContext getGLContext();

  static glm::ivec4 getDisplayRect(Uint32 index = 0);

  static void pythonBindings(py::module& m);

private:
  static SDL_GLContext _glContext;
};