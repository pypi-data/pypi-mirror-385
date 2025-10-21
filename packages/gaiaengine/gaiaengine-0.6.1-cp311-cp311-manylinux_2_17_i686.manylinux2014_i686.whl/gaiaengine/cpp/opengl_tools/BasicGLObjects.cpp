#include "BasicGLObjects.h"

void VertexBufferObject::cpuBufferSubData(std::vector<float>& bufferData, size_t offset, size_t size, const void* data) {
  const float* floatData = (const float*) data;

  for (int i = 0; i < size; i++) {
    bufferData[i + offset] = floatData[i];
  }
}
