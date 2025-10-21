// This file is the custom implementation of the file "imconfig.h" from the imgui library folder that is used in gaiaengine

#pragma once

#include <glm/glm.hpp>

#define IMGUI_IMPL_OPENGL_LOADER_CUSTOM "opengl.h"

#define IM_VEC2_CLASS_EXTRA \
    constexpr ImVec2(const glm::vec2& f) : x(f.x), y(f.y) {} \
    operator glm::vec2() const { return glm::vec2(x, y); } \
    constexpr ImVec2(const glm::ivec2& f) : x((float)f.x), y((float)f.y) {} \
    operator glm::ivec2() const { return glm::ivec2((int)x, (int)y); } \
    constexpr ImVec2(const glm::uvec2& f) : x((float)f.x), y((float)f.y) {} \
    operator glm::uvec2() const { return glm::uvec2((unsigned int)x, (unsigned int)y); }

#define IM_VEC4_CLASS_EXTRA \
        constexpr ImVec4(const glm::vec4& f) : x(f.x), y(f.y), z(f.z), w(f.w) {} \
        operator glm::vec4() const { return glm::vec4(x,y,z,w); } \
        constexpr ImVec4(const glm::ivec4& f) : x((float)f.x), y((float)f.y), z((float)f.z), w((float)f.w) {} \
        operator glm::ivec4() const { return glm::ivec4((int)x, (int)y, (int)z, (int)w); } \
        constexpr ImVec4(const glm::uvec4& f) : x((float)f.x), y((float)f.y), z((float)f.z), w((float)f.w) {} \
        operator glm::uvec4() const { return glm::uvec4((unsigned int)x, (unsigned int)y, (unsigned int)z, (unsigned int)w); }
