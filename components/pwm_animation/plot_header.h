#pragma once

#include <stdint.h>

namespace AnimationData {

enum class AnimationType : uint16_t;
enum class CustomAnimationVersion : uint8_t;
using AnimationThresholdType = uint8_t;

struct CustomAnimationInfo {
  uint32_t signature;
  uint16_t crc16;
  uint16_t total_size;
  CustomAnimationVersion header_version;
  int8_t name_length;
  int16_t name_offset;
  int16_t thresholds_offset;
  int16_t thresholds_length;
  const char data[0];
};

struct AnimationInfo {
  const AnimationThresholdType *data;
  int length;
  const char *name;
};

static constexpr uint32_t kCustomAnimationSignature = 1398030659;

enum class CustomAnimationVersion : uint8_t {
  Invalid = 0,
  Current = sizeof(CustomAnimationInfo),
  Version_1 = 16,
};

}  // namespace AnimationData