#pragma once

#include <opengl.h>

#include "GLObject.h"
#include "utils.h"

#include <memory>
#include <string>

class Program : public GLObject<Program> {
public:
  template<GLenum ShaderType>
  class Shader : public GLObject<Shader<ShaderType>> {
  public:
    Shader(const std::string& sourceFile) : GLObject<Shader>() {
      std::string absolutePath = GAIA_SOURCE_PATH + std::string("/shaders/") + sourceFile;
      std::string sourceCode = ut::textFileToString(absolutePath);

      const GLchar* str = sourceCode.c_str();
      const char* sources[2] = { getGLSLVersion().c_str(), str };

      glShaderSource(GLObject<Shader>::getObjectID(), 2, sources, 0);
      glCompileShader(GLObject<Shader>::getObjectID());

      GLint compilationError(0);
      glGetShaderiv(GLObject<Shader>::getObjectID(), GL_COMPILE_STATUS, &compilationError);

      if (compilationError != GL_TRUE) {
        GLint errorLength(0);
        glGetShaderiv(GLObject<Shader>::getObjectID(), GL_INFO_LOG_LENGTH, &errorLength);
        std::string error(errorLength, '\0');
        glGetShaderInfoLog(GLObject<Shader>::getObjectID(), errorLength, &errorLength, error.data());
        error.resize(errorLength);

        throw std::runtime_error((sourceFile + std::string(": Error in shader compilation: ") + error).c_str());
      }
    }

  private:
    static void genObject(GLuint& objectID) { objectID = glCreateShader(ShaderType); };
    static void bindObject(GLuint /*objectID*/) { /* Shaders are used through programs, not by themselves */ };
    static void deleteObject(GLuint objectID) { glDeleteShader(objectID); };

    friend class GLObject<Shader>;
  };

  Program(const std::string& vertexSourceFile, const std::string& fragmentSourceFile, const std::string& geometrySourceFile = std::string());

  inline GLint getUniformLocation(const GLchar* name) const { return glGetUniformLocation(getObjectID(), name); }

  inline static const std::string& getGLSLVersion() { return glslVersion; }

private:
  static void genObject(GLuint& objectID) { objectID = glCreateProgram(); };
  static void bindObject(GLuint objectID) { glUseProgram(objectID); };
  static void deleteObject(GLuint objectID) { glDeleteProgram(objectID); };

  friend class GLObject;

  static std::string glslVersion;

  Shader<GL_VERTEX_SHADER> _vertex;
  Shader<GL_FRAGMENT_SHADER> _fragment;
  std::unique_ptr<Shader<GL_GEOMETRY_SHADER>> _geometry;
};
