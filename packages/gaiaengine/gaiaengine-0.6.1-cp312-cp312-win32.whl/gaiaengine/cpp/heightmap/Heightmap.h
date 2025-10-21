#pragma once

#include <glm/glm.hpp>

#include "BasicGLObjects.h"
#include "Color.h"
#include "Component.h"
#include "Program.h"

#include <memory>
#include <unordered_map>
#include <vector>

class Texture;

// Vertex coordinates and cell coordinates
// 0,0 --- 0,1 --- 0,2
//  |  0,0  |  0,1  |
// 1,0 --- 1,1 --- 1,2
//  |  1,0  |  1,1  |
// 2,0 --- 2,1 --- 2,2

class Heightmap : public Component {
public:
  Heightmap(std::shared_ptr<Window> window, const glm::ivec2& nbCells);
  Heightmap(std::shared_ptr<Window> window, const glm::ivec2& nbCells, std::vector<float> heights);
  Heightmap(std::shared_ptr<Window> window, const glm::ivec2& nbCells, std::vector<float> heights, std::vector<int> textureIDs);

  void updateVisuals(int /*msElapsed*/, const Camera*) override;
  void render(const Camera* camera) const override;

  // Returns the index that is associated with the texture path. Loads the texture if necessary
  int loadTexture(const std::string& path);
  std::shared_ptr<Texture> getTexture(int index) const;
  void bindTexture(int index) const;

  glm::vec2 getMaxCoordinates() const { return glm::vec2(getNbCells()); }
  inline bool isOutsideBounds(const glm::vec2& pos) const {
    return pos.x < 0.f || pos.y < 0.f || pos.x >= getMaxCoordinates().x || pos.y >= getMaxCoordinates().y;
  }

  // Returns whether the position was actually updated or not
  bool teleportPositionOnOtherSideIfOutside(glm::vec2& position) const;

  inline bool areInvalidCellCoordinates(const glm::ivec2& coord) const {
    return coord.x < 0 || coord.y < 0 || coord.x >= getNbCells().x || coord.y >= getNbCells().y;
  }

  inline bool areInvalidVertexCoordinates(const glm::ivec2& coord) const {
    return coord.x < 0 || coord.y < 0 || coord.x >= getNbVertices().x || coord.y >= getNbVertices().y;
  }

  inline glm::ivec2 getNbCells() const { return _nbVertices - 1; }
  inline glm::ivec2 getNbVertices() const { return _nbVertices; }

  inline void resize(const glm::ivec2& nbCells) { resize(glm::ivec4(0, 0, nbCells)); }
  void resize(const glm::ivec4& newRect);

  inline const std::vector<bool>& getNavigation() const { return _isNavigable; }
  void setNavigation(std::vector<bool> isNavigable);
  bool getIsNavigable(const glm::vec2& pos) const;
  void setIsNavigable(const glm::ivec2& cellCoordinates, bool isNavigable);

  inline virtual const std::vector<float>& getHeights() const { return _heights; }
  inline virtual void setHeights(std::vector<float> heights) { _heights = std::move(heights); _geometryDirty = true; }
  float getHeight(const glm::vec2& pos) const;
  void setHeight(const glm::ivec2& vertCoordinates, float height);

  inline const std::vector<int>& getTextureIDs() const { return _textureIDs; }
  inline void setTextureIDs(std::vector<int> textureIDs) { _textureIDs = std::move(textureIDs); _textureIDsDirty = true; }
  int getTextureID(const glm::vec2& pos) const;
  void setTextureID(const glm::ivec2& cellCoordinates, int textureID);

  inline const std::vector<Color>& getColors() const { return _colors; }
  inline void setColors(std::vector<Color> colors) { _colors = std::move(colors); _geometryDirty = true; }
  Color getColor(const glm::vec2& pos) const;
  void setColor(const glm::ivec2& vertCoordinates, const Color& color);

  std::shared_ptr<Texture> getTexture(const glm::vec2& pos) const { return getTexture(getTextureID(pos)); }

  glm::vec3 getVertexNormal(const glm::ivec2& vertCoordinates) const;
  glm::vec3 getCellNormal(const glm::vec2& pos) const;
  
  inline glm::vec3 getOriginOffset() const { return _originOffset; }
  inline void setOriginOffset(glm::vec3 val) { _originOffset = val; }

  inline bool getSmoothNormals() const { return _smoothNormals; }
  void setSmoothNormals(bool val);

  inline bool getSmoothColors() const { return _smoothColors; }
  void setSmoothColors(bool val);

  static void pythonBindings(py::module& m);

private:
  void generateGeometry();
  void computeVertexNormals();
  void computeCellNormals();
  void generateTextureMapping();

  bool _wireframe = false;

  std::vector<std::shared_ptr<Texture>> _textures;
  Program _shader;

  glm::ivec2 _nbVertices = glm::ivec2(-1);
  std::vector<float> _heights;
  std::vector<glm::vec3> _vertexNormals;
  std::vector<glm::vec3> _cellNormals;
  std::vector<Color> _colors;
  std::vector<int> _textureIDs;
  std::vector<bool> _isNavigable;
  glm::vec3 _originOffset = glm::vec3(0.f);

  bool _noNormalInShader = false;
  bool _smoothNormals = true;
  bool _smoothColors = false;

  bool _geometryDirty = false;
  bool _textureIDsDirty = false;

  // Buffers
  VertexArrayObject _vao;
  VertexBufferObject _vbo;
  std::unordered_map<int, IndexBufferObject> _ibos;

  // Data
  std::unordered_map<int, std::vector<int>> _indicesPerTexture;
};