import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.core import coroutine_with_priority, CORE
from esphome import automation, controller
from esphome.components.mqtt import MQTTClientComponent, MQTTMessage
from esphome.components import logger
from esphome.components.pca9685 import PCA9685Output
from esphome.components import web_server, light
from esphome.cpp_helpers import setup_entity
from esphome.const import (
    CONF_WEB_SERVER,
)
import re

DEPENDENCIES = ["pca9685"]
AUTO_LOAD = ["output"]

COMPONENT_CLASS = "cat4anna/pwm_animation"

class CONFIG:
    ID = "id"
    PWM_ID = "pwm_id"
    CHANNELS = "channels"
    CHANNELS_ID = "channels_id"

pwm_anim_ns = cg.esphome_ns.namespace("pwm_animation")
PWMAnimation = pwm_anim_ns.class_("PWMAnimation", cg.Component)
PWMChannelArray = pwm_anim_ns.class_("PWMChannelArray")

def check_channels(value):
    if isinstance(value, int):
        return [value]

    if isinstance(value, str):
        result = []
        for item in value.split(","):
            groups = re.match(r"(\d+)(\-(\d+))?", item)
            if groups.group(3):
                for i in range(int(groups.group(1)), int(groups.group(3)) + 1):
                    result.append(i)
            else:
                result.append(int(groups.group(1)))

        return result

    raise cv.Invalid(f"Invalid format for channels config value")

CONFIG_SCHEMA = cv.All(
    cv.ENTITY_BASE_SCHEMA
    .extend(web_server.WEBSERVER_SORTING_SCHEMA)
    .extend(controller.gen_component_schema(COMPONENT_CLASS))
    .extend(
        {
            cv.GenerateID(CONFIG.ID): cv.declare_id(PWMAnimation),
            cv.GenerateID(CONFIG.CHANNELS_ID): cv.declare_id(PWMChannelArray),
            cv.GenerateID(CONFIG.PWM_ID): cv.use_id(PCA9685Output),
            cv.Required(CONFIG.CHANNELS): check_channels
        }
    )
    # .extend(cv.COMPONENT_SCHEMA)
)

@coroutine_with_priority(45.0)
async def to_code(config):
    pca = await cg.get_variable(config[CONFIG.PWM_ID])

    channels = config[CONFIG.CHANNELS]
    anim_channels = cg.new_Pvariable(config[CONFIG.CHANNELS_ID])
    cg.add(anim_channels.resize(len(channels)))

    for index in range(len(channels)):
        cg.add(anim_channels.at(index).set_channel(channels[index]))
        cg.add(pca.register_channel(anim_channels.get_ptr(index)))

    anim_driver = cg.new_Pvariable(config[CONFIG.ID], anim_channels)
    await setup_entity(anim_driver, config)
    await cg.register_component(anim_driver, config)

    if web_server_config := config.get(CONF_WEB_SERVER):
        await web_server.add_entity_config(anim_driver, web_server_config)

    await controller.setup_component(COMPONENT_CLASS, anim_driver, config)

