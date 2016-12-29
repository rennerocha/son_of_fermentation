# pip install adafruit_python_dht
import time

import Adafruit_DHT
import paho.mqtt.client as mqtt

DHT_TYPE = Adafruit_DHT.DHT11
DHT_PIN = 8
FREQUENCY_SECONDS = 30


def start(mqtt_settings):
    mqtcc = mqtt.Client('CHAMBER', clean_session=False)

    mqtcc.username_pw_set(
        mqtt_settings.get('MQTT_BROKER_USERNAME'),
        mqtt_settings.get('MQTT_BROKER_PASSWORD')
    )
    mqtcc.connect(
        mqtt_settings.get('MQTT_BROKER_HOST'),
        mqtt_settings.get('MQTT_BROKER_PORT'),
        60
    )
    mqtcc.loop_start()

    while True:
        humidity, temperature = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
        if humidity is None or temperature is None:
            continue

        mqtcc.publish(
            'myownbrewery/chamber/temperature',
            temperature
        )
        mqtcc.publish(
            'myownbrewery/chamber/humidity',
            humidity
        )

        time.sleep(FREQUENCY_SECONDS)

    mqtcc.disconnect()
