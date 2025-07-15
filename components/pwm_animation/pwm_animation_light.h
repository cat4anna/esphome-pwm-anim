#pragma once

#include <vector>
#include <chrono>

#include "esphome/core/defines.h"
#include "esphome/core/component.h"

#include "esphome/components/pca9685/pca9685_output.h"
#include "esphome/core/component.h"

#if __has_include("esphome/components/light/light_output.h")
#include "esphome/components/output/binary_output.h"
#include "esphome/components/light/light_output.h"
#define USE_PWM_ANIM_LIGHT_OUTPUT
#endif

#include "animation_driver.h"

namespace esphome::pwm_animation
{
#ifdef USE_PWM_ANIM_LIGHT_OUTPUT

    // TODO

    class PWMAnimationLightOutput : public light::LightOutput
    {
    public:
        void set_output(output::BinaryOutput *output) { output_ = output; }
        light::LightTraits get_traits() override
        {
            auto traits = light::LightTraits();
            traits.set_supported_color_modes({light::ColorMode::ON_OFF});
            return traits;
        }
        void write_state(light::LightState *state) override
        {
            bool binary;
            state->current_values_as_binary(&binary);
            if (binary)
            {
                this->output_->turn_on();
            }
            else
            {
                this->output_->turn_off();
            }
        }

    protected:
        output::BinaryOutput *output_;
    };

#else

    class PWMAnimationLightOutput
    {
    };

#endif
}
