#pragma once

#include <vector>
#include <chrono>

#include "esphome/core/component.h"

#include "esphome/components/pwm_animation/pwm_animation.h"
#include "esphome/components/mqtt_homie/homie_node.h"

namespace esphome::pwm_animation {

class PWMAnimation;

class HomieNodePWMAnimation : public mqtt_homie::HomieNodeMultiProperty {
 public:
  static constexpr auto TAG = "homie:PWMAnimation";

  HomieNodePWMAnimation(PWMAnimation *pwm_animation);

 protected:
  PWMAnimation *m_pwm_animation;
  const esphome::EntityBase *GetEntityBase() const override;
  const esphome::EntityBase_DeviceClass *GetEntityBaseDeviceClass() const override;

  std::string m_animation_list;
  std::string m_custom_animation_encoded;

  void init_animation_list();
  void init_properties();
  void load_custom_animation(const std::string &value);
};
}  // namespace esphome::pwm_animation
