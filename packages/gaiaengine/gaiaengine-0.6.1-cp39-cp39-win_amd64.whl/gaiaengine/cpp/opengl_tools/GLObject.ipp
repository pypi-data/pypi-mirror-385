#pragma once

#include "Context.h"

#include <stdexcept>

template<class Derived>
GLObject<Derived>::GLObject() {
  if (!Context::isGLContextValid())
    throw std::runtime_error("Trying to access OpenGL functions without having a valid gl context. Please create a Window.");

  Derived::genObject(_objectID);
}

template<class Derived>
GLObject<Derived>::GLObject(GLObject<Derived>&& other) noexcept {
  *this = std::move(other);
}

template<class Derived>
GLObject<Derived>& GLObject<Derived>::operator=(GLObject&& other) noexcept {
  Derived::deleteObject(_objectID);
  _objectID = other._objectID;
  other._objectID = 0;

  return *this;
}

template<class Derived>
GLObject<Derived>::~GLObject() {
  Derived::deleteObject(_objectID);
}

template<class Derived>
GLObjectBinder<Derived> GLObject<Derived>::scopeBind() const {
  return GLObjectBinder<Derived>(*this);
}