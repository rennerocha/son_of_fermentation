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
        mqtt_settings.get('username'),
        mqtt_settings.get('password')
    )
    mqtcc.connect(
        mqtt_settings.get('host'),
        mqtt_settings.get('port'),
        60
    )
    mqtcc.loop_start()

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
        if humidity is not None and temperature is not None:
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
