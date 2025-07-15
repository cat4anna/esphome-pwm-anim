#pragma once

#include <stdint.h>

#include "plot_header.h"

namespace esphome::pwm_animation {

  using namespace AnimationData;

struct AnimationDriver {
  AnimationDriver();

  void SetAnimation(const AnimationThresholdType *thresholds, uint16_t thresholds_count);
  void SetChannels(uint8_t count, uint8_t span = 0);

  AnimationThresholdType SamplePWM(uint8_t channel, uint16_t position);
  uint16_t GetPosition(float time);

  void GetCurrentPWMValues(float time, AnimationThresholdType *values);

 private:
  uint8_t channel_count = 8;
  uint8_t channel_span = 128 / 32;

  const AnimationThresholdType *thresholds = nullptr;
  uint16_t thresholds_count = 0;
};
}  // namespace esphome::pwm_animation