#pragma once

#include <opengl.h>

#include <functional>

#define CONCAT_IMPL( x, y ) x##y
#define MACRO_CONCAT( x, y ) CONCAT_IMPL( x, y )
#define SCOPE_BIND(X) auto MACRO_CONCAT(_GLObject_scope_bind_, __LINE__) = X.scopeBind();
#define SCOPE_BIND_PTR(X) auto MACRO_CONCAT(_GLObject_scope_bind_, __LINE__) = X->scopeBind();

template <class Derived>
class GLObjectBinder;

// Base class to encapsulate the management of OpenGL resources for many typical OpenGL objects
// Usage:
// Override GLObject and declare 3 static functions to create, bind and delete the object
// Make them private and make GLObject a friend of the derived class to make sure it's the only one to have access to those
// Example for textures:
// 
// static void genObject(GLuint& objectID) { glGenTextures(1, &objectID); };
// static void bindObject(GLuint objectID) { glBindTexture(GL_TEXTURE_2D, objectID); };
// static void deleteObject(GLuint objectID) { glDeleteTextures(1, &objectID); };
//
// friend class GLObject;
template <class Derived> 
class GLObject {
public:
  GLObject();

  // Deleting the copy operator as internal gl resources should only be managed by one instance of the class
  // And we don't have access to the actual resources to copy them
  GLObject (GLObject const&) = delete;
  GLObject& operator=(GLObject const&) = delete;

  GLObject(GLObject&& other) noexcept;
  GLObject& operator=(GLObject&& other) noexcept;
  virtual ~GLObject();

  GLObjectBinder<Derived> scopeBind() const;
  inline void bind() const { Derived::bindObject(_objectID); }
  inline static void unbind() { Derived::bindObject(0); }

  GLuint getObjectID() const { return _objectID; }

private:
  GLuint _objectID = 0;
};

// Small helper to simplify the calls to bind and unbind
// The bound GLObject object must always extend the binder's lifetime
template <class Derived>
class [[nodiscard("The object will be unbound instantly. Use the SCOPE_BIND macro.")]] GLObjectBinder {
public:
  GLObjectBinder(const GLObject<Derived>& glObject) { glObject.bind(); }

  GLObjectBinder(GLObjectBinder const&) = default;
  GLObjectBinder& operator=(GLObjectBinder const&) = default;
  GLObjectBinder(GLObjectBinder&& other) = default;
  GLObjectBinder& operator=(GLObjectBinder&& other) = default;

  ~GLObjectBinder() { GLObject<Derived>::unbind(); }

private:
  friend class GLObject<Derived>;
};

#include "GLObject.ipp"
