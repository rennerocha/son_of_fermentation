# -*- coding: utf-8 -*-
import logging
import os
import time

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import requests
import w1thermsensor

KEEP_ALIVE_SEC = 3600  # One minute

FAN_PIN = 7
STATUS = {
    'running': True,
    'setpoint': 20.0,
    'tolerance': 0.5,
    'fan': GPIO.LOW,
    'temperature': 0.0
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('son_of_fermentation.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('Client connected. Subscribing to messages.')


def log_reading(temperature, fan_status):
    # https://thingspeak.com/channels/154653
    THINGSPEAK_CHANNEL_API_KEY = '1VDKH5HU2D7C6347'
    THINGSPEAK_URL = 'https://api.thingspeak.com/update'
    thingspeak_values = {
        'api_key': THINGSPEAK_CHANNEL_API_KEY,
        'field1': temperature,
        'field2': fan_status,
    }
    requests.get(THINGSPEAK_URL, params=thingspeak_values)


def on_connect(client, userdata, flags, rc):
    global STATUS

    logger.info('Client connected. Subscribing to messages.')

    client.subscribe('myownbrewery/son_of_fermentation/stop')
    client.subscribe('myownbrewery/son_of_fermentation/temperature/setpoint')

    # Inform other client of the initial status of the fermenter
    client.publish(
        'myownbrewery/son_of_fermentation/temperature', STATUS['temperature']
    )
    client.publish(
        'myownbrewery/son_of_fermentation/temperature/setpoint', STATUS['setpoint']
    )
    client.publish(
        'myownbrewery/son_of_fermentation/fan', STATUS['fan']
    )


def on_disconnect(client, userdata, rc):
    logger.info('Client disconnected.')


def on_message(client, userdata, message):
    global STATUS

    logger.info('Message received: {0}'.format(message.topic))
    logger.info('Message content: {0}'.format(message.payload))

    if message.topic == 'myownbrewery/son_of_fermentation/temperature/setpoint':
        try:
            new_setpoint = int(message.payload)
            logger.info('New temperature setpoint: {0}'.format(new_setpoint))
        except:
            pass
        else:
            STATUS['setpoint'] = new_setpoint
    elif message.topic == 'myownbrewery/son_of_fermentation/stop':
        STATUS['running'] = False


def start(mqtt_settings, running=True):
    global STATUS
    logger.info('Starting son_of_fermentation.')

    mqtcc = mqtt.Client('SON_OF_FERMENTATION', clean_session=False)

    mqtcc.on_connect = on_connect
    mqtcc.on_disconnect = on_disconnect
    mqtcc.on_message = on_message

    mqtcc.username_pw_set(
        mqtt_settings.get('username'),
        mqtt_settings.get('password')
    )
    mqtcc.connect(
        mqtt_settings.get('host'),
        mqtt_settings.get('port'),
        keepalive=KEEP_ALIVE_SEC
    )
    mqtcc.loop_start()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, GPIO.LOW)
    sensor = w1thermsensor.W1ThermSensor()

    logger.info('Initial temperature setpoint: {0}'.format(STATUS['setpoint']))
    while STATUS['running']:
        last_reading = sensor.get_temperature()
        mqtcc.publish(
            'myownbrewery/son_of_fermentation/temperature',
            last_reading
        )
        logger.info('Temperature reading: {0}'.format(last_reading))

        if last_reading > STATUS['setpoint'] + STATUS.get('tolerance', 0.5):
            fan_status = GPIO.HIGH
            GPIO.output(FAN_PIN, GPIO.HIGH)
            logger.info('Temperature higher than desired. Turning fan on.')
        else:
            fan_status = GPIO.LOW
            GPIO.output(FAN_PIN, GPIO.LOW)
            logger.info('Temperature below desired. Turning fan off.')

        if STATUS['fan'] != fan_status:
            STATUS['fan'] = fan_status
            mqtcc.publish(
                'myownbrewery/son_of_fermentation/fan', STATUS['fan'])

        log_reading(last_reading, STATUS['fan'])

        time.sleep(30)

    logger.info('Stopping son_of_fermentation.')
    GPIO.cleanup()
    mqtcc.disconnect()


def main():
    MQTT_BROKER_HOST = 'broker.myownbrewery.com'
    MQTT_BROKER_PORT = 8883
    MQTT_BROKER_USERNAME = os.environ.get('MQTT_BROKER_USERNAME', '')
    MQTT_BROKER_PASSWORD = os.environ.get('MQTT_BROKER_PASSWORD', '')

    mqtt_settings = {
        'host': MQTT_BROKER_HOST,
        'port': MQTT_BROKER_PORT,
        'username': MQTT_BROKER_USERNAME,
        'password': MQTT_BROKER_PASSWORD,
    }

    try:
        start(mqtt_settings)
    except:
        logger.exception('Something wrong happened.')


if __name__ == '__main__':
    time.sleep(30)
    main()
