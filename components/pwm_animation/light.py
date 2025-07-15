import esphome.codegen as cg
from esphome.components import light, output
import esphome.config_validation as cv
from esphome.components import light, output
from esphome.const import CONF_OUTPUT, CONF_OUTPUT_ID

from . import PWMAnimation

pwm_anim_ns = cg.esphome_ns.namespace("pwm_animation")
PWMAnimationLightOutput = pwm_anim_ns.class_("PWMAnimationLightOutput", cg.Component)

CONFIG_SCHEMA = light.BINARY_LIGHT_SCHEMA.extend(
    {
        cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(PWMAnimationLightOutput),
        cv.GenerateID(CONF_OUTPUT): cv.use_id(PWMAnimation),
    }
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    await light.register_light(var, config)

    out = await cg.get_variable(config[CONF_OUTPUT])
    cg.add(var.set_output(out))