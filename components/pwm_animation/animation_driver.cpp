#include <chrono>
#include "animation_driver.h"

namespace esphome::pwm_animation {

AnimationDriver::AnimationDriver() {}

void AnimationDriver::SetAnimation(const AnimationThresholdType *thresholds, uint16_t thresholds_count) {
  this->thresholds = thresholds;
  this->thresholds_count = thresholds_count;
  SetChannels(channel_count);
}

void AnimationDriver::SetChannels(uint8_t count, uint8_t span) {
  channel_count = count;
  if (span == 0)
    channel_span = thresholds_count / count;
  else
    channel_span = span;
}

AnimationThresholdType AnimationDriver::SamplePWM(uint8_t channel, uint16_t position) {
  uint16_t index = position + static_cast<uint16_t>(channel) * static_cast<uint16_t>(channel_span);
  return thresholds[index % thresholds_count];
}

uint16_t AnimationDriver::GetPosition(float time) { return static_cast<uint16_t>(time) % thresholds_count; }

void AnimationDriver::GetCurrentPWMValues(float time, AnimationThresholdType *values) {
  if (!values || !thresholds)
    return;

  auto pos = GetPosition(time);

  for (uint8_t i = 0; i < channel_count; ++i) {
    values[i] = SamplePWM(i, pos) ;
  }
}

}  // namespace esphome::pwm_animation