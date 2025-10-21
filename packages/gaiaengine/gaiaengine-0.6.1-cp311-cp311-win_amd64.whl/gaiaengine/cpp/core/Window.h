#pragma once

#include <glm/glm.hpp>
#include <SDL.h>

#include "Component.h"
#include "Clock.h"
#include "Manager.h"
#include "TexturedRectangle.h"

#include <memory>
#include <vector>

#include <pybind11/pybind11.h>

namespace py = pybind11;

class Camera;
class EventManager;

/*
 * Handles the whole lifetime of a simulation and its different systems
 */

class Window : public Manager<Component> {
public:
  Window(glm::ivec2 windowSize, Uint32 windowFlags = 0);
  Window(glm::ivec4 windowScreenRect = glm::ivec4(SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, -1, -1), Uint32 windowFlags = 0);
  Window(Window const&) = delete;
  void operator=(Window const&) = delete;

  void requestClose();
  // Parameter to only run a given number of frames
  void run(int nbSteps = -1);

  // Display and input frame time, independent from the one used for running simulations
  inline int getFrameTime() const { return _msCurrentFrameTime; }
  inline int getAbsoluteTime() const { return Clock::getAbsoluteTime(); }

  inline int getMsSimulationStep() const { return _msSimulationStep; }
  inline int getSimulationTime() const { return _msElapsedSimTime; }
  inline float getSimulationSpeedFactor() const { return _simulationSpeedFactor; }
  inline int getMsFrameTimeRender() const { return _msFrameTimeRender; }
  inline float getMinFPSForAcceleratedSim() const { return _minFPSForAcceleratedSim; }

  inline std::shared_ptr<Camera> getCamera() const { return _camera; }
  void setCamera(std::shared_ptr<Camera> newCamera);

  inline SDL_Window* getSDLWindow() const { return _windowSDL; }

  glm::ivec2 getWindowSize() const;
  void setWindowSize(const glm::ivec2& newSize);

  float getDPIZoom() const;

  static void pythonBindings(py::module& m);
private:
  void close();
  
  bool _running = false;
  bool _wantsToStop = false;

  int _msCurrentFrameTime = 0;
  int _msSimulationStep = 16;
  int _msElapsedSimTime = 0;
  float _simulationSpeedFactor = 1.f;
  int _msFrameTimeRender = 0;
  // Give a negative value to disable it
  float _minFPSForAcceleratedSim = 30.f;
  bool _paused = false;

  float _accumulatedSimTime = 0.f;

  float _currentFPS = 0.f;
  
  std::shared_ptr<Camera> _camera;
  std::unique_ptr<const TexturedRectangle> _screenTexture;
  std::shared_ptr<EventManager> _eventManager;

  SDL_Window* _windowSDL = nullptr;
};