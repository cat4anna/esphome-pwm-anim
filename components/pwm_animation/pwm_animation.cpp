#include "pwm_animation.h"

#include "esphome/core/log.h"
#include "generated_plots.h"

namespace esphome::pwm_animation {

namespace {

const AnimationInfo *get_animation_info(AnimationType type) {
  if (type == AnimationType::Custom)
    return nullptr;

  if (type >= AnimationType::Count)
    type = AnimationType::Default;

  unsigned index = static_cast<unsigned>(type);
  return &kAnimationArray[index];
}

void dump_custom_anim(const CustomAnimationInfo *header) {
  static constexpr auto TAG = "PWMAnimation.custom";

  if (header == nullptr) {
    ESP_LOGI(TAG, "No custom PWM animation");
    return;
  }

  ESP_LOGI(TAG, "Custom PWM animation setup completed:");
  ESP_LOGI(TAG, "Signature: %u", header->signature);
  ESP_LOGI(TAG, "crc16: %u", header->crc16);
  ESP_LOGI(TAG, "total_size: %u", header->total_size);
  ESP_LOGI(TAG, "header_version: %u", header->header_version);
  ESP_LOGI(TAG, "name_length: %u", header->name_length);
  ESP_LOGI(TAG, "name_offset: %u", header->name_offset);
  ESP_LOGI(TAG, "thresholds_offset: %u", header->thresholds_offset);
  ESP_LOGI(TAG, "thresholds_length: %u", header->thresholds_length);

  std::string d;
  int offset = 0;
  d.reserve(256);
  const uint16_t *ptr = reinterpret_cast<const uint16_t *>(header->data + header->thresholds_offset);
  for (int i = 0, c = 0; i < header->thresholds_length; ++i) {
    char b[16];
    sprintf(b, "%04x", ptr[i]);
    d += b;
    ++c;

    if (c == 16) {
      ESP_LOGI(TAG, "data[%04x]: %s", offset, d.c_str());
      c = 0;
      d.clear();
      offset = i;
    }
    if (c > 0 && (c % 4) == 0) {
      d += " ";
    }
  }
  if (!d.empty()) {
    ESP_LOGI(TAG, "data[%04x]: %s", offset, d.c_str());
  }
}

}  // namespace

PWMAnimation::PWMAnimation(PWMChannelArray *chanels) : m_chanels(*chanels), m_animation(AnimationType::Default) {
  m_update_time = Clock_t::now();
  m_animation_driver.SetChannels(m_chanels.size());
  init_animation(AnimationType::Default);
}

void PWMAnimation::loop() {
  if (!m_enabled) {
    return;
  }

  const int channel_count = m_chanels.size();
  AnimationThresholdType values[kMaxChannels] = {};

  auto now = Clock_t::now();
  auto micros = std::chrono::duration_cast<std::chrono::microseconds>(now - m_update_time).count();
  if (micros < 10 * 1000) {
    return;
  }

  float dt = std::chrono::duration<float>(now - m_update_time).count();
  m_position += dt * m_speed * kSpeedScale;

  m_update_time = now;

  m_animation_driver.GetCurrentPWMValues(m_position, values);

  float data[kMaxChannels] = {};
  for (int i = 0; i < channel_count; ++i) {
    const float value = values[i] / 255.0f;
    data[i] = value * m_intensity;
  }
  set_channels(data);
}

void PWMAnimation::set_channels(const float *data) {
  const int channel_count = m_chanels.size();
  for (int i = 0; i < channel_count; ++i) {
    m_chanels[i].set_level(data[i]);
  }
}

void PWMAnimation::set_enbled(bool b) {
  m_enabled = b;
  if (!m_enabled) {
    float data[kMaxChannels] = {};
    set_channels(data);
  } else {
    m_update_time = Clock_t::now();
  }
}

void PWMAnimation::init_animation(AnimationType type) {
  m_animation = type;
  ESP_LOGI(TAG, "Setting animation to %d", (int) type);

  if (m_animation == AnimationType::Custom) {
    auto info = get_custom_animation_header();
    if (info != nullptr) {
      auto data = info->data + info->thresholds_offset;
      m_animation_driver.SetAnimation(reinterpret_cast<const AnimationThresholdType *>(data), info->thresholds_length);
    }
  } else {
    auto info = get_animation_info(type);
    m_animation_driver.SetAnimation(info->data, info->length);
  }
}

const char *PWMAnimation::get_animation_name() {
  if (m_animation == AnimationType::Custom)
    return "Custom";
  auto info = get_animation_info(m_animation);
  if (info != nullptr)
    return info->name;
  return "";
}

void PWMAnimation::set_animation_by_name(const std::string &name) {
  ESP_LOGI(TAG, "Setting animation to %s", name.c_str());
  for (unsigned i = 0; i < kAnimationArray.size(); ++i)
    if (str_equals_case_insensitive(name, kAnimationArray[i].name)) {
      init_animation(static_cast<AnimationType>(i));
      return;
    }

  if (str_equals_case_insensitive(name, "Custom")) {
    init_animation(AnimationType::Custom);
    return;
  }
}

std::vector<std::string> PWMAnimation::get_all_animations() {
  std::vector<std::string> r;
  for (auto &item : kAnimationArray)
    r.emplace_back(item.name);
  return r;
}

std::string PWMAnimation::get_custom_animation_name() const {
  auto custom_animation = get_custom_animation_header();
  if (!custom_animation)
    return "";

  const char *data = custom_animation->data + custom_animation->name_offset;
  return std::string(data, data + custom_animation->name_length);
}

const CustomAnimationInfo *PWMAnimation::get_custom_animation_header() const {
  if (m_custom_animation_data.empty())
    return nullptr;
  return reinterpret_cast<const CustomAnimationInfo *>(&m_custom_animation_data[0]);
}

bool PWMAnimation::set_custiom_animation_data(std::vector<uint8_t> data) {
  if (data.empty()) {
    m_custom_animation_data = {};
    return true;
  }

  if (data.size() < sizeof(CustomAnimationInfo)) {
    ESP_LOGW(TAG, "Custom PWM an1imation setup failed: too small data");
    return false;
  }

  auto header = reinterpret_cast<CustomAnimationInfo *>(&data[0]);
  if (header->signature != kCustomAnimationSignature || header->header_version != CustomAnimationVersion::Current ||
      header->total_size != data.size()) {
    ESP_LOGW(TAG, "Custom PWM animation setup failed: malformed data");
    return false;
  }

  //   auto crc = header->crc16;
  //   header->crc16 = 0;

  m_custom_animation_data.swap(data);
  dump_custom_anim(get_custom_animation_header());
  if (m_animation == AnimationType::Custom) {
    init_animation(m_animation);
  }

  return true;
}

}  // namespace esphome::pwm_animation
