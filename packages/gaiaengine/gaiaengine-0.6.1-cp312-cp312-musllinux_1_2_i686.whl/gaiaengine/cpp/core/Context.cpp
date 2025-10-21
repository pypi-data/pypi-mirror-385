#include "Context.h"

#include <opengl.h>
#include <SDL_image.h>

#include <cstdlib>
#include <cstring>
#include <ctime>
#include <sstream>

SDL_GLContext Context::_glContext = 0;

Context::Context() {
  srand((unsigned int)time(NULL));

  SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Initializing Gaia Engine");

  // Setting Gaia to support Windows high DPI screens by default
  if (!SDL_GetHint(SDL_HINT_WINDOWS_DPI_AWARENESS))
    SDL_SetHint(SDL_HINT_WINDOWS_DPI_AWARENESS, "permonitorv2");

  if (SDL_Init(SDL_INIT_VIDEO) < 0)
    throw std::runtime_error((std::string("SDL could not initialize! ") + std::string(SDL_GetError())).c_str());

  static constexpr int imgFlags = IMG_INIT_PNG;
  if ((IMG_Init(imgFlags) & imgFlags) != imgFlags)
    throw std::runtime_error((std::string("SDL_image could not initialize! ") + std::string(IMG_GetError())).c_str());
}

bool Context::wasSDLInitialized() {
  return SDL_WasInit(SDL_INIT_VIDEO) != 0;
}

bool Context::isGLContextValid() {
  return _glContext != 0;
}

void Context::setWindow(SDL_Window* window) {
  if (!window) {
    _glContext = 0;
  }
  else if (!isGLContextValid()) {
    _glContext = SDL_GL_CreateContext(window);

    if (!isGLContextValid())
      throw std::runtime_error(std::string(SDL_GetError()));

    const char* obtainedGLVersion = (const char*)glGetString(GL_VERSION);
    if (obtainedGLVersion == nullptr)
      throw std::runtime_error("OpenGL was not loaded properly, unable to get version");

    constexpr char targetGLVersion[] = "3.3";
    if (strcmp(obtainedGLVersion, targetGLVersion) < 0) {
      std::stringstream errorInfo;
      errorInfo << "\nThe requested OpenGL version is unavailable: Requested " << targetGLVersion << " and got " << obtainedGLVersion
        << std::endl << "Please check your graphics drivers";
      throw std::runtime_error(errorInfo.str());
    }

#ifdef _WIN32
    if (glewInit() != GLEW_OK)
      throw std::runtime_error("Failed to initialize GLEW");
#endif
  }
}

SDL_GLContext Context::getGLContext() {
  return _glContext;
}

glm::ivec4 Context::getDisplayRect(Uint32 index) {
  SDL_DisplayMode displayMode;
  SDL_GetDesktopDisplayMode(index, &displayMode);
  
  return glm::ivec4(0, 0, displayMode.w, displayMode.h);
}

Context::~Context() {
  SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Shutting down Gaia Engine");

  if (isGLContextValid())
    SDL_GL_DeleteContext(_glContext);

  IMG_Quit();
  SDL_Quit();
}

void Context::pythonBindings(py::module& m) {
  py::class_<Context>(m, "Context")
    .def(py::init<>())
    .def_static("getDisplayRect", &Context::getDisplayRect, py::arg("index") = 0);
}