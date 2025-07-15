#include "pwm_animation_homie.h"
#include "esphome/core/helpers.h"

#include "esphome/core/log.h"

namespace esphome::pwm_animation {

HomieNodePWMAnimation::HomieNodePWMAnimation(PWMAnimation *pwm_animation) : m_pwm_animation(pwm_animation) {
  init_animation_list();
  init_properties();
}

void HomieNodePWMAnimation::init_animation_list() {
  m_animation_list.clear();
  m_animation_list.reserve(512);
  for (auto &item : m_pwm_animation->get_all_animations()) {
    if (!m_animation_list.empty())
      m_animation_list += ",";
    m_animation_list += item;
  }
  if (!m_animation_list.empty())
    m_animation_list += ",";
  m_animation_list += "Custom";
  m_animation_list.shrink_to_fit();
}

void HomieNodePWMAnimation::load_custom_animation(const std::string &value) {
  if (value.empty()) {
    m_pwm_animation->set_custiom_animation_data({});
    m_custom_animation_encoded = "";
    return;
  }
  m_custom_animation_encoded = value;

  auto decoded = base64_decode(m_custom_animation_encoded);
  if (m_pwm_animation->set_custiom_animation_data(std::move(decoded))) {
    notify_property_changed("custom_animation_name");
  } else {
    //
  }
}

void HomieNodePWMAnimation::init_properties() {
  using PropertyDescriptor = mqtt_homie::PropertyDescriptor;

  PropertyDescriptor speed = {
      .id = "speed",
      .name = "Speed",
      // todo - range -10-10 ?
      .datatype = homie::datatype::number,
      .getter = [this] { return std::to_string(m_pwm_animation->get_speed()); },
      .setter =
          [this](const std::string &value) {
            float f = parse_number<float>(value.c_str()).value_or(1.0f);
            f = clamp(f, -10.0f, 10.0f);
            m_pwm_animation->set_speed(f);
          },
  };
  PropertyDescriptor brightness = {
      .id = "brightness",
      .name = "Brightness",
      // todo - range 0-1 ?
      .datatype = homie::datatype::number,
      .getter = [this] { return std::to_string(m_pwm_animation->get_intensity()); },
      .setter =
          [this](const std::string &value) {
            auto f = parse_number<float>(value.c_str()).value_or(1.0f);
            f = clamp(f, -0.0f, 1.0f);
            m_pwm_animation->set_intensity(f);
          },
  };

  PropertyDescriptor enabled = {
      .id = "enabled",
      .name = "Enabled",
      .datatype = homie::datatype::boolean,
      .getter = [this] { return m_pwm_animation->get_enabled() ? "true" : "false"; },
      .setter =
          [this](const std::string &value) {
            if (str_equals_case_insensitive(value, "toggle")) {
              m_pwm_animation->set_enbled(!m_pwm_animation->get_enabled());
            } else {
              m_pwm_animation->set_enbled(str_equals_case_insensitive(value, "true"));
            }
          },
  };

  PropertyDescriptor animation = {
      .id = "animation",
      .name = "Animation",
      .format = m_animation_list.c_str(),
      .datatype = homie::datatype::string,
      .getter = [this] { return std::string(m_pwm_animation->get_animation_name()); },
      .setter = [this](const std::string &value) { m_pwm_animation->set_animation_by_name(value); },
  };

  PropertyDescriptor custom_animation = {
      .id = "custom_animation",
      .name = "Custom Animation",
      .datatype = homie::datatype::string,
      .getter = [this] { return m_custom_animation_encoded; },
      .setter = [this](const std::string &value) { load_custom_animation(value); },
  };
  PropertyDescriptor custom_animation_name = {
      .id = "custom_animation_name",
      .name = "Custom Animation Name",
      .datatype = homie::datatype::string,
      .getter = [this] { return m_pwm_animation->get_custom_animation_name(); },
      .setter = nullptr,
  };

  create_properties({
      std::move(speed),
      std::move(brightness),
      std::move(enabled),
      std::move(animation),
      std::move(custom_animation),
      std::move(custom_animation_name),
  });
}

const esphome::EntityBase *HomieNodePWMAnimation::GetEntityBase() const { return m_pwm_animation; }

const esphome::EntityBase_DeviceClass *HomieNodePWMAnimation::GetEntityBaseDeviceClass() const {
  return m_pwm_animation;
}

}  // namespace esphome::pwm_animation
