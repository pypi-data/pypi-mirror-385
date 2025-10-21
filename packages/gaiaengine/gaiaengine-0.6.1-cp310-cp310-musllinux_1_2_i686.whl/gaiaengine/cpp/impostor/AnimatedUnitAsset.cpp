#include "AnimatedUnitAsset.h"

AnimatedUnitAsset::AnimatedUnitAsset(const std::vector<std::string>& assetPaths, const std::vector<float>& animDurations, const std::vector<float>& replayDelays):
  UnitAsset(assetPaths)
{
  // If the anim durations are not specified yet, they'll get their default on loading,
  // since it will depend on the number of frames
  if (animDurations.size() != 0)
    _animDurations = animDurations;

  _replayDelays.resize(assetPaths.size());

  for (int i = 0; i < replayDelays.size(); i++) {
    _replayDelays[i] = (int) (replayDelays[i] * 1000);
  }
}

void AnimatedUnitAsset::load() {
  UnitAsset::load();

  for (int i = 0; i < _spriteInfo.size(); i++) {
    int nbSteps = (int) _spriteInfo[i].size() / 5;

    // TODO make orientation handling more generic
    // Hack: if there is only one sprite, it means that it's a static picture and we don't want to generate the additional orientations
    if (_spriteInfo[i].size() == 1)
      continue;

    // 8 orientations, we need to manually fill the 3 missing
    _spriteInfo[i].resize(nbSteps * 8);

    // The missing 3 orientations are horizontally flipped copies of the others
    for (int j = 0; j < nbSteps; j++) {
      _spriteInfo[i][5 * nbSteps + j] = _spriteInfo[i][3 * nbSteps + j].getFlippedCopy();
      _spriteInfo[i][6 * nbSteps + j] = _spriteInfo[i][2 * nbSteps + j].getFlippedCopy();
      _spriteInfo[i][7 * nbSteps + j] = _spriteInfo[i][1 * nbSteps + j].getFlippedCopy();
    }
  }

  if (_animDurations.size() == 0) {
    _animDurations.resize(_assetPaths.size());
    for (int i = 0; i < _animDurations.size(); i++) {
      _animDurations[i] = getNbSteps(i) / 25.f; // Default of 25 FPS for an unspecified animation
    }
  }
}

int AnimatedUnitAsset::getClosestOrientation(float orientation) const {
  float orientationStep = 360.f / (float)getNbOrientations();

  return (getNbOrientations() - (int)(round(orientation / orientationStep) + 0.5f)) % getNbOrientations();
}

#include <pybind11/stl.h>

void AnimatedUnitAsset::pythonBindings(py::module& m) {
  py::class_<AnimatedUnitAsset, std::shared_ptr<AnimatedUnitAsset>, UnitAsset>(m, "AnimatedUnitAsset")
    .def(py::init<const std::vector<std::string>&, const std::vector<float>&, const std::vector<float>&>())
    .def("getNbSteps", &AnimatedUnitAsset::getNbSteps)
    .def("getFrameDurationMs", &AnimatedUnitAsset::getFrameDurationMs)
    .def("getReplayDelay", &AnimatedUnitAsset::getReplayDelay)
    .def("getAnimDuration", &AnimatedUnitAsset::getAnimDuration)
    .def_readwrite("animDurations", &AnimatedUnitAsset::_animDurations)
    .def_readwrite("replayDelays", &AnimatedUnitAsset::_replayDelays);
}