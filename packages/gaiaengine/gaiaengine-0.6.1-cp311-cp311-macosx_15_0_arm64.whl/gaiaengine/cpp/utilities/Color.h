#pragma once

#include <glm/glm.hpp>
#include <SDL.h>

#include <string>
#include <tuple>

#include <pybind11/pybind11.h>

namespace py = pybind11;

// Small container for a 32 bits RGBA color that can be converted to other useful formats 
class Color {
public:
  Color() = default;
  Color(const std::string& hexColorCode);
  Color(const SDL_Color& color);
  Color(float r_, float g_, float b_);
  Color(float r_, float g_, float b_, float a_);
  Color(Uint8 r_, Uint8 g_, Uint8 b_);
  Color(Uint8 r_, Uint8 g_, Uint8 b_, Uint8 a_);

  inline float getFloatR() const { return (float)r / 255.f; }
  inline float getFloatG() const { return (float)g / 255.f; }
  inline float getFloatB() const { return (float)b / 255.f; }
  inline float getFloatA() const { return (float)a / 255.f; }
  inline float setFloatR(float r_) { return r = (Uint8)(r_ * 255); }
  inline float setFloatG(float g_) { return g = (Uint8)(g_ * 255); }
  inline float setFloatB(float b_) { return b = (Uint8)(b_ * 255); }
  inline float setFloatA(float a_) { return a = (Uint8)(a_ * 255); }

  inline glm::ivec3 getRGB() const { return glm::ivec3(r, g, b); }
  inline glm::ivec4 getRGBA() const { return glm::ivec4(r, g, b, a); }
  inline glm::vec3 getRGBFloat() const { return glm::vec3(getFloatR(), getFloatG(), getFloatB()); }
  inline glm::vec4 getRGBAFloat() const { return glm::vec4(getFloatR(), getFloatG(), getFloatB(), getFloatA()); }
  inline std::tuple<Uint8, Uint8, Uint8> getRGBTuple() const { return std::make_tuple(r, g, b); }
  inline std::tuple<Uint8, Uint8, Uint8, Uint8> getRGBATuple() const { return std::make_tuple(r, g, b, a); }
  inline std::tuple<float, float, float> getRGBTupleFloat() const { return std::make_tuple(getFloatR(), getFloatG(), getFloatB()); }
  inline std::tuple<float, float, float, float> getRGBATupleFloat() const { return std::make_tuple(getFloatR(), getFloatG(), getFloatB(), getFloatA()); }

  inline void setRGB(const glm::ivec3& v) { r = (Uint8)v.r; g = (Uint8)v.g; b = (Uint8)v.b; }
  inline void setRGBA(const glm::ivec4& v) { r = (Uint8)v.r; g = (Uint8)v.g; b = (Uint8)v.b; a = (Uint8)v.a; }
  inline void setRGBFloat(const glm::vec3& v) { setFloatR(v.r); setFloatG(v.g); setFloatB(v.b); }
  inline void setRGBAFloat(const glm::vec4& v) { setFloatR(v.r); setFloatG(v.g); setFloatB(v.b); setFloatA(v.a); }
  inline void setRGBTuple(std::tuple<Uint8, Uint8, Uint8> tuple) { 
    r = std::get<0>(tuple); g = std::get<1>(tuple); b = std::get<2>(tuple); 
  }
  inline void setRGBATuple(std::tuple<Uint8, Uint8, Uint8, Uint8> tuple) {
    r = std::get<0>(tuple); g = std::get<1>(tuple); b = std::get<2>(tuple); a = std::get<3>(tuple);
  }
  inline void setRGBTupleFloat(std::tuple<float, float, float> tuple) { 
    setFloatR(std::get<0>(tuple)); setFloatG(std::get<1>(tuple)); setFloatB(std::get<2>(tuple)); 
  }
  inline void setRGBATupleFloat(std::tuple<float, float, float, float> tuple) {
    setFloatR(std::get<0>(tuple)); setFloatG(std::get<1>(tuple)); setFloatB(std::get<2>(tuple)); setFloatA(std::get<3>(tuple));
  }

  Uint8 r = 0, g = 0, b = 0, a = 0;

  bool operator==(const Color& other) const { return r == other.r && g == other.g && b == other.b && a == other.a; }

  static void pythonBindings(py::module& m);
};