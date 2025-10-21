#include "Window.h"

#include <opengl.h>

#include "Camera.h"
#include "Context.h"
#include "EventManager.h"

Window::Window(glm::ivec2 windowSize, Uint32 windowFlags) :
  Window(glm::ivec4(SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, windowSize.x, windowSize.y), windowFlags)
{}

Window::Window(glm::ivec4 windowScreenRect, Uint32 windowFlags)
{
  if (!Context::wasSDLInitialized())
    throw std::runtime_error("Trying to create a window without having initialized Gaia, please create a Context object in the same scope as the window");

  SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);

// This is needed on Linux because it defaults to 3.0 otherwise, despite asking for a core profile
#ifdef __linux__
  SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
  SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
#endif

  if (windowScreenRect.z < 0)
    windowScreenRect.z = (int)((float)1024 * getDPIZoom());
  if (windowScreenRect.w < 0)
    windowScreenRect.w = (int)((float)768 * getDPIZoom());

  SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Creating window");

  _windowSDL = SDL_CreateWindow("Gaia Engine", windowScreenRect.x, windowScreenRect.y, windowScreenRect.z, windowScreenRect.w,
    SDL_WINDOW_OPENGL | windowFlags);

  if (!_windowSDL)
    throw std::runtime_error((std::string("Unable to create SDL Window: ") + std::string(SDL_GetError())).c_str());

  Context::setWindow(_windowSDL);

  // Enable VSync by default
  SDL_GL_SetSwapInterval(1);

  glDepthFunc(GL_LEQUAL);
  glEnable(GL_DEPTH_TEST);
  glCullFace(GL_BACK);
  glEnable(GL_CULL_FACE);
  glLineWidth(getDPIZoom());
  
  setCamera(std::make_shared<Camera>());
}

void Window::run(int nbSteps) {
  if (_running)
    throw std::runtime_error("Cannot call Window::run while the window is already running. Try using a Timer instead");

  Clock frameClock;
  _running = true;

  SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Running");

  try {
    while (!_wantsToStop && nbSteps != 0) {
      _msCurrentFrameTime = frameClock.getElapsedTime();

      if (!_paused)
        _accumulatedSimTime += _msCurrentFrameTime * _simulationSpeedFactor;

      float simulationSpeedFactorUsedThisFrame = _simulationSpeedFactor;

      frameClock.restart();

      int requestedSimIterations = (int)(_accumulatedSimTime / (float)_msSimulationStep);
      for (int i = 0; i < requestedSimIterations; i++) {
        _accumulatedSimTime -= (float)_msSimulationStep;
        _msElapsedSimTime += _msSimulationStep;

        for (auto& component : getElements()) {
          component->update(_msSimulationStep);
        }

        if (nbSteps != -1) {
          nbSteps--;

          if (nbSteps == 0)
            break;
        }

        int projectedNextStepElapsedTime = i == 0 ? frameClock.getElapsedTime() : frameClock.getElapsedTime() * (i + 1) / i;
        if ((_minFPSForAcceleratedSim > 0 && projectedNextStepElapsedTime + _msFrameTimeRender > 1000.f / _minFPSForAcceleratedSim) ||
          _simulationSpeedFactor != simulationSpeedFactorUsedThisFrame) {
          // Discard all remaining planned steps this frame
          _accumulatedSimTime -= (float)(requestedSimIterations - i - 1) * _msSimulationStep;
          break;
        }
      }

      int beforeRenderTimeMs = frameClock.getElapsedTime();

      _camera->apply(_msCurrentFrameTime);

      for (auto& component : getElements()) {
        component->updateVisuals(_msCurrentFrameTime, _camera.get());
      }

      _camera->renderComponents(getElements());

      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
      _screenTexture->render();

      SDL_GL_SwapWindow(_windowSDL);
      _msFrameTimeRender = frameClock.getElapsedTime() - beforeRenderTimeMs;
    }
  }
  catch (...) {
    close();
    throw;
  }

  close();
}

glm::ivec2 Window::getWindowSize() const {
  glm::ivec2 windowSize;
  SDL_GetWindowSize(_windowSDL, &windowSize.x, &windowSize.y);
  return windowSize;
}

void Window::setWindowSize(const glm::ivec2& newSize) {
  SDL_SetWindowSize(_windowSDL, newSize.x, newSize.y);
  _camera->setViewportSize(newSize);
}

float Window::getDPIZoom() const {
#ifdef _WIN32
  const float systemDefaultDPI = 96.f;
  float dpi;
  if (SDL_GetDisplayDPI(0, NULL, &dpi, NULL) != 0)
  {
    // Failed to get DPI, so just return the default value.
    dpi = systemDefaultDPI;
  }
  return dpi / systemDefaultDPI;
#else

  // High DPI support for other platforms will come when moving to SDL3
  return 1.f;
#endif
}

void Window::setCamera(std::shared_ptr<Camera> newCamera) {
  if (newCamera.get() == nullptr)
    throw std::invalid_argument("Invalid Camera object");

  _camera = newCamera;
  _camera->setViewportSize(getWindowSize());
  _screenTexture = std::make_unique<TexturedRectangle>(_camera->getColorBuffer());
}

void Window::requestClose() {
  SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Requested close");
  _wantsToStop = true;
}

void Window::close() {
  SDL_LogInfo(SDL_LOG_CATEGORY_APPLICATION, "Closing window");
  _running = false;
  _wantsToStop = false;

  Context::setWindow(nullptr);

  if (_windowSDL)
    SDL_DestroyWindow(_windowSDL);
}

void Window::pythonBindings(py::module& m) {
  py::class_<Window, std::shared_ptr<Window>, ManagerBase>(m, "Window_")
    .def(py::init<glm::ivec2, Uint32>(),
      py::arg("windowSize"),
      py::arg("windowFlags") = 0)
    .def(py::init<glm::ivec4, Uint32>(),
      py::arg("windowScreenRect") = glm::ivec4(SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, -1, -1),
      py::arg("windowFlags") = 0)
    .def("run", &Window::run, py::arg("nbSteps") = -1)
    .def("close", &Window::requestClose)
    .def_property("windowSize", &Window::getWindowSize, &Window::setWindowSize)
    .def_property_readonly("dpiZoom", &Window::getDPIZoom)
    .def_property("camera", &Window::getCamera, &Window::setCamera)
    .def("getSDLWindow", [](const Window& w) {return (uintptr_t)w.getSDLWindow(); })
    .def_property_readonly("frameTime", &Window::getFrameTime)
    .def_property_readonly("absoluteTime", &Window::getAbsoluteTime)
    .def_readwrite("simulationStepTime", &Window::_msSimulationStep)
    .def_property_readonly("simulationTime", &Window::getSimulationTime)
    .def_readwrite("simulationSpeedFactor", &Window::_simulationSpeedFactor)
    .def_readwrite("minFPSForAcceleratedSim", &Window::_minFPSForAcceleratedSim)
    .def_readwrite("paused", &Window::_paused);
}