#pragma once

#include <glm/glm.hpp>

class TargetInterface {
public:
  virtual glm::vec2 getScaledDirection() const { return glm::vec2(0.f); }
  virtual glm::vec2 getPosition() const = 0;
  virtual bool isValid() const { return true; }
};

class StaticTarget : public TargetInterface {
public:
  StaticTarget(const glm::vec2& position) : _position(position) {}

  glm::vec2 getPosition() const override { return _position; }

private:
  glm::vec2 _position = glm::vec2(-1.f);
};