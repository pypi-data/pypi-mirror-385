#include "Program.h"

#include <sstream>

std::string Program::glslVersion = "#version 330\n";

Program::Program(const std::string& vertexSourceFile, const std::string& fragmentSourceFile, const std::string& geometrySourceFile):
  GLObject(),
  _vertex(vertexSourceFile),
  _fragment(fragmentSourceFile)
{
  glAttachShader(getObjectID(), _vertex.getObjectID());
  glAttachShader(getObjectID(), _fragment.getObjectID());

  if (!geometrySourceFile.empty()) {
    _geometry = std::make_unique<Shader<GL_GEOMETRY_SHADER>>(geometrySourceFile);
    glAttachShader(getObjectID(), _geometry->getObjectID());
  }

  glLinkProgram(getObjectID());

  GLint errorLink(0);
  glGetProgramiv(getObjectID(), GL_LINK_STATUS, &errorLink);
  if (errorLink != GL_TRUE) {
    GLint errorLength(0);
    glGetProgramiv(getObjectID(), GL_INFO_LOG_LENGTH, &errorLength);
    std::string error(errorLength, '\0');
    glGetShaderInfoLog(getObjectID(), errorLength, &errorLength, error.data());
    error.resize(errorLength);

    std::ostringstream oss;
    if (_geometry)
      oss << "(" << vertexSourceFile << "," << fragmentSourceFile << "," << geometrySourceFile
        << "): Error in shader linking: " << error;
    else
      oss << "(" << vertexSourceFile << "," << fragmentSourceFile
        << "): Error in shader linking: " << error;
    
    throw std::runtime_error(oss.str());
  }
}
