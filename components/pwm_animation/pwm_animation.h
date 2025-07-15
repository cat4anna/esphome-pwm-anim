#pragma once

#include <vector>
#include <chrono>

#include "esphome/core/defines.h"
#include "esphome/core/component.h"
#include "esphome/core/entity_base.h"

#include "esphome/components/pca9685/pca9685_output.h"

#include "pwm_animation_light.h"
#include "animation_driver.h"

#include "plot_header.h"

namespace esphome::pwm_animation {

using namespace ::AnimationData;

static constexpr unsigned kMaxChannels = 16;

class PWMChannelArray : public std::vector<esphome::pca9685::PCA9685Channel> {
 public:
  esphome::pca9685::PCA9685Channel *get_ptr(int index) { return &at(index); }
};

class PWMAnimation : public EntityBase, public EntityBase_DeviceClass, public Component {
 public:
  static constexpr auto TAG = "PWMAnimation";

  float speed = 1.0;

  static constexpr float kSpeedScale = 100;

  PWMAnimation(PWMChannelArray *chanels);

  void loop() override;

  using Clock_t = std::chrono::steady_clock;

  void set_speed(float f) { m_speed = f; }
  float get_speed() { return m_speed; }

  void set_intensity(float f) { m_intensity = f; }
  float get_intensity() { return m_intensity; }

  void set_enbled(bool b);
  bool get_enabled() { return m_enabled; }

  const char *get_animation_name();
  void set_animation_by_name(const std::string &name);
  std::vector<std::string> get_all_animations();

  std::string get_custom_animation_name() const;
  bool set_custiom_animation_data(std::vector<uint8_t> data);

 protected:
  bool m_enabled = true;
  float m_intensity = 1.0;
  float m_speed = 1.0;
  float m_position = 0;
  AnimationType m_animation;
  std::vector<uint8_t> m_custom_animation_data;

  Clock_t::time_point m_update_time;
  AnimationDriver m_animation_driver;
  PWMChannelArray &m_chanels;

  void set_channels(const float *data);
  void init_animation(AnimationType type);

  const CustomAnimationInfo *get_custom_animation_header() const;
};
}  // namespace esphome::pwm_animation
