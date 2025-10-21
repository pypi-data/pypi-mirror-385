#pragma once

#include "UnitAsset.h"

#include <map>
#include <string>

/** One instance that will load the textures and metadata used commonly by
  * UnitAnimationHandler instances.
  */
class AnimatedUnitAsset : public UnitAsset {
public:
  AnimatedUnitAsset(const std::vector<std::string>& assetPaths, const std::vector<float>& animDurations = {}, const std::vector<float>& replayDelays = {});

  void load() override;

  inline int getNbSteps(int texture) const { return (int) _spriteInfo[texture].size() / getNbOrientations(); }
  // 5 actual orientations for SLPs, the three last being mirrored
  // TODO make orientation handling more generic
  // Hack to allow supporting single textures with only one orientation
  inline int getNbOrientations() const { return _spriteInfo[0].size() == 1 ? 1 : 8; }
  int getClosestOrientation(float orientation) const;
  inline int getFrameDurationMs(int texture) const { return (int) (_animDurations[texture] * 1000 / getNbSteps(texture)); }
  inline int getReplayDelay(int texture) const { return _replayDelays[texture]; }
  inline float getAnimDuration(int texture) const { return _animDurations[texture]; }

  static void pythonBindings(py::module& m);

private:
  std::vector<float> _animDurations;
  std::vector<int> _replayDelays;
};
