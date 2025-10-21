#include "UnitRenderer.h"

#include <glm/gtx/vector_angle.hpp>

#include "Camera.h"
#include "Unit.h"
#include "TextureArray.h"

#include <cmath>

UnitRenderer::UnitRenderer() {
  setUnitNearPlane(2.f);
}

void UnitRenderer::setUnitNearPlane(float val) {
  _unitNearPlane = val;
  SCOPE_BIND(_unitShader)
  glUniform1f(_unitShader.getUniformLocation("elementNearPlane"), getUnitNearPlane());
}

glm::mat4 UnitRenderer::getModelMatrix(const Camera* camera) const {
  glm::vec3 toCamera = -camera->getCurrentDirection();

  glm::mat4 rotateUnits = glm::rotate(glm::mat4(1.f),
    glm::orientedAngle(glm::vec2(1.f, 0.f), glm::normalize(glm::vec2(toCamera.x, toCamera.y))),
    glm::vec3(0, 0, 1));

  // - pi/2 to make the face rather than the edge face the camera
  // We divide by 2 afterwards to have the rotation from the center of the unit rather than the bottom
  rotateUnits = glm::rotate(rotateUnits,
    (glm::angle(glm::vec3(0.f, 0.f, 1.f), toCamera) - (float)M_PI / 2.f) / 2.f,
    glm::vec3(0, 1, 0));

  return rotateUnits;
}

void UnitRenderer::fillBufferData(GLenum renderType) {
  if (_data.size() == 0)
    return;

  SCOPE_BIND(_vbo)

  glBufferData(GL_ARRAY_BUFFER, _data.size() * sizeof(float), &_data[0], renderType);

  SCOPE_BIND(_ibo)

  std::vector<GLuint> indices(6*_capacity);

  for (int i = 0; i < _capacity; i++) {
    indices[6*i]     = 0 + 4*i;
    indices[6*i + 1] = 1 + 4*i;
    indices[6*i + 2] = 2 + 4*i;
    indices[6*i + 3] = 0 + 4*i;
    indices[6*i + 4] = 2 + 4*i;
    indices[6*i + 5] = 3 + 4*i;
  }

  glBufferData(GL_ELEMENT_ARRAY_BUFFER, _capacity * 6 * sizeof(indices[0]), &indices[0], GL_STATIC_DRAW);

  SCOPE_BIND(_vao)

  int sizeFloatValue = _capacity * 4 * sizeof(float);

  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(0));
  glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(sizeFloatValue * 3));
  glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(sizeFloatValue * 6));
  glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(sizeFloatValue * 8));
  glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(sizeFloatValue * 9));

  glEnableVertexAttribArray(0);
  glEnableVertexAttribArray(1);
  glEnableVertexAttribArray(2);
  glEnableVertexAttribArray(3);
  glEnableVertexAttribArray(4);
}

void UnitRenderer::processSpree(const std::vector<std::shared_ptr<Unit>>& unitsToDisplay,
  int currentSpreeLength, int firstIndexSpree) {

  if (currentSpreeLength != 0) { // otherwise first call, there is no spree yet

    _textures.push_back(unitsToDisplay[firstIndexSpree]->getTextureArray());
    _nbUnitsInSpree.push_back(currentSpreeLength);

    for (int i = firstIndexSpree; i < firstIndexSpree + currentSpreeLength; i++) {
      const std::array<float, 12>& vertices = unitsToDisplay[i]->getVertices();
      const std::array<float, 12>& posArray = unitsToDisplay[i]->getPositionArray();
      const std::array<float,  8>& coord2D = unitsToDisplay[i]->getCoord2D();
      const std::array<float,  4>& layer = unitsToDisplay[i]->getLayer();
      const std::array<float, 12>& heightmapNormal = unitsToDisplay[i]->getHeightmapNormal();

      std::copy(vertices.begin(),        vertices.end(),        _data.begin() + i*12);
      std::copy(posArray.begin(),        posArray.end(),        _data.begin() + _capacity*12 + i*12);
      std::copy(coord2D.begin(),         coord2D.end(),         _data.begin() + _capacity*24 + i*8);
      std::copy(layer.begin(),           layer.end(),           _data.begin() + _capacity*32 + i*4);
      std::copy(heightmapNormal.begin(), heightmapNormal.end(), _data.begin() + _capacity*36 + i*12);
    }
  }
}

void UnitRenderer::loadUnits(const std::vector<std::shared_ptr<Unit>>& visibleUnits, bool onlyOnce) {
  _textures.clear();
  _nbUnitsInSpree.clear();

  _capacity = (int) visibleUnits.size();
  _data.resize(_capacity * 48);

  int currentSpreeLength = 0;
  int firstIndexSpree = 0;

  const TextureArray* currentTexture = nullptr;

  for (int i = 0; i < visibleUnits.size(); i++) {
    if (currentTexture != visibleUnits[i]->getTextureArray()) {
      processSpree(visibleUnits, currentSpreeLength, firstIndexSpree);
      currentTexture = visibleUnits[i]->getTextureArray();
      firstIndexSpree += currentSpreeLength;
      currentSpreeLength = 0;
    }

    currentSpreeLength++;
  }

  processSpree(visibleUnits, currentSpreeLength, firstIndexSpree);

  if (onlyOnce)
    fillBufferData(GL_STATIC_DRAW);
  else
    fillBufferData(GL_DYNAMIC_DRAW);
}

void UnitRenderer::render(const Camera* camera) const {
  glm::mat4 MVP = camera->getViewProjectionMatrix();

  glm::mat4 rotateUnits = getModelMatrix(camera);

  SCOPE_BIND(_unitShader)
    glUniformMatrix4fv(_unitShader.getUniformLocation("VP"),
      1, GL_FALSE, &MVP[0][0]);
  glUniformMatrix4fv(_unitShader.getUniformLocation("MODEL"),
    1, GL_FALSE, &rotateUnits[0][0]);
  glUniform3fv(_unitShader.getUniformLocation("camPos"),
    1, &camera->getCurrentPosition()[0]);

  // Two passes to avoid artifacts due to alpha blending

  glUniform1i(_unitShader.getUniformLocation("onlyOpaqueParts"), true);
  renderPass();

  glUniform1i(_unitShader.getUniformLocation("onlyOpaqueParts"), false);

  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  renderPass();

  glDisable(GL_BLEND);
}

int UnitRenderer::renderPass() const {
  int cursor = 0;

  SCOPE_BIND(_vao)
  SCOPE_BIND(_ibo)

  for (int i = 0; i < _nbUnitsInSpree.size(); i++) {
    SCOPE_BIND_PTR(_textures[i])

    glDrawElements(GL_TRIANGLES, 6 * _nbUnitsInSpree[i], GL_UNSIGNED_INT, BUFFER_OFFSET(cursor * sizeof(GLuint)));

    cursor += 6 * _nbUnitsInSpree[i];
  }

  glDisable(GL_POLYGON_OFFSET_FILL);

  return cursor / 6;
}
