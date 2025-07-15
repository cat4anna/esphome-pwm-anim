import paho.mqtt.client as mqtt
import random


class MQTTHandler:
    broker = 'cabbit.lan'
    port = 1883
    client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def __init__(self, print_status):
        self.print_status = lambda m: print_status(f"MQTT: {m}")
        self.__init_connection()

    def __init_connection(self):
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.client_id)
        mqtt_client.on_message = self.on_mqtt_message
        mqtt_client.on_connect = self.on_mqtt_connect
        mqtt_client.on_disconnect = self.on_mqtt_disconnect

        self.mqtt_client = mqtt_client

        self.print_status(f"Connecting to {self.broker}:{self.port}")
        mqtt_client.connect(self.broker, self.port)
        mqtt_client.loop_start()

    def on_mqtt_connect(self, mqtt_client, obj, flags, reason_code, properties):
        self.print_status("Connected")

    def on_mqtt_message(mqtt_client, obj, msg):
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        pass

    def on_mqtt_disconnect(self, *a, **kw):
        self.print_status("Disconnected")

    def check_status(self):
        if self.mqtt_client.is_connected():
            self.print_status("Ready")

    def homie_set(self, node, payload, dev_name = "pwm_anim_test", prefix="test"):
        topic = f"{prefix}/{dev_name}/pwm_animation/{node}/set"
        info = self.mqtt_client.publish(topic, payload)
        # info.wait_for_publish()
        self.print_status(f"Published {topic}")

