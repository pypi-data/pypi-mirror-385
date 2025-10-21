#pragma once

#include <glm/glm.hpp>

#include "Color.h"
#include "TextureArray.h"

#include <memory>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>

namespace py = pybind11;

struct SDL_Palette;
struct SDL_Surface;

struct SpriteInfo {
  int x = 0, y = 0;
  int w = 0, h = 0;
  int anchor_x = 0, anchor_y = 0;

  SpriteInfo() = default;
  SpriteInfo(int width, int height):
    w(width),
    h(height),
    anchor_x(width/2),
    anchor_y(height)
  {}
  SpriteInfo(int x_, int y_, int w_, int h_, int ax_, int ay_) : x(x_), y(y_), w(w_), h(h_), anchor_x(ax_), anchor_y(ay_) {}

  SpriteInfo getFlippedCopy() const {
    return SpriteInfo{ x + w, y, -w, h, w - anchor_x, anchor_y };
  }
};

// Lazily loaded unit asset reference
// Gets loaded when asked or when an unit is created using it
class UnitAsset {
public:
  UnitAsset() = default;
  UnitAsset(const Color& color, const glm::ivec2& size);

  // The provided texture can either be a full path to an image,
  // or a full path to a sprite sheet + the os separator + a full path to a text file containing the sprites pixels info
  UnitAsset(const std::string& assetPath);
  UnitAsset(const std::vector<std::string>& assetPaths);

  inline bool isLoaded() const { return _textureArray.get() && _textureArray->getCount() == _assetPaths.size(); }
  virtual void load();

  static std::shared_ptr<SDL_Surface> loadSpriteSheet(const std::string& texturePath, const std::string& infoFilePath, std::vector<SpriteInfo>& currentSprites);
  static std::shared_ptr<SDL_Surface> loadSLP(const std::string& filePath, std::vector<SpriteInfo>& currentSprites);

  inline bool textureExists(int textureID) const { return textureID >= 0 && textureID < _textureArray->getCount() && !_assetPaths[textureID].empty(); }

  inline const TextureArray* getTextureArray() const { return _textureArray.get(); }
  virtual glm::vec4 getTexRectangle(int textureID, int spriteID) const;

  inline const SpriteInfo& getCurrentSpriteInfo(int texture, int sprite) const { return _spriteInfo[texture][sprite]; }
  inline const std::vector<std::vector<SpriteInfo>>& getSpriteInfo() const { return _spriteInfo; }

  inline int getMaxAnchorHeight() const { return _maxAnchorHeight; }

  static void pythonBindings(py::module& m);

protected:
  std::vector<std::string> _assetPaths;
  std::vector<std::vector<SpriteInfo>> _spriteInfo;

private:
  static void processSLPDrawingCommands(std::shared_ptr<SDL_Surface> surface, std::shared_ptr<SDL_Palette> palette, std::ifstream& input, int startPixelX, int startPixelY);
  static std::shared_ptr<SDL_Palette> selectPalette(uint32_t paletteID);

  static std::vector<std::shared_ptr<SDL_Palette>> Palettes;

  int _maxAnchorHeight = 0;
  // Can be used to store an ID for this asset. Represents the AoE unit ID when loaded from an AoE asset
  int _unitID = -1;

  Color _fallbackColor = Color(0.f, 0.f, 0.f);
  glm::ivec2 _fallbackSize = glm::ivec2(20, 30);
  std::unique_ptr<TextureArray> _textureArray;
};