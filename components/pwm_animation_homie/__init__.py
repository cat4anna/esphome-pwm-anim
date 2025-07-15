import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.core import coroutine_with_priority, CORE
from esphome import automation, controller
from esphome.components.mqtt import MQTTClientComponent, MQTTMessage
from esphome.components import logger
from esphome.components.pca9685 import PCA9685Output
# from esphome-homie.components.homie_mqtt import HomieNodeBase
# from ..pwm_animation import COMPONENT_CLASS

COMPONENT_CLASS = "cat4anna/pwm_animation"
DEPENDENCIES = ["mqtt_homie"]

pwm_animation_ns = cg.esphome_ns.namespace("pwm_animation")
HomieNodePWMAnimation = pwm_animation_ns.class_("HomieNodePWMAnimation", cg.Component)

class HomeNode:
    CLASS_TYPE = {
        COMPONENT_CLASS: HomieNodePWMAnimation
    }


controller.get_controller("homie").register_node_class(HomeNode())

CONFIG_SCHEMA = cv.All()

@coroutine_with_priority(45.0)
async def to_code(config):
    # cg.add_library("zlib...")
    pass
