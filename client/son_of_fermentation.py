# -*- coding: utf-8 -*-
import time

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import w1thermsensor

FAN_PIN = 7
STATUS = {
    'running': True,
    'setpoint': 20.0,
    'tolerance': 0.5,
    'fan': GPIO.LOW,
    'temperature': 0.0
}


def on_connect(client, userdata, flags, rc):
    global STATUS

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
    pass


def on_message(client, userdata, message):
    global STATUS

    if message.topic == 'myownbrewery/son_of_fermentation/temperature/setpoint':
        try:
            new_setpoint = int(message.payload)
        except:
            pass
        else:
            STATUS['setpoint'] = new_setpoint
    elif message.topic == 'myownbrewery/son_of_fermentation/stop':
        STATUS['running'] = False


def start(mqtt_settings, running=True):
    global STATUS

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
        60
    )
    mqtcc.loop_start()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, GPIO.LOW)
    sensor = w1thermsensor.W1ThermSensor()

    while STATUS['running']:
        last_reading = sensor.get_temperature()
        mqtcc.publish(
            'myownbrewery/son_of_fermentation/temperature',
            last_reading
        )

        if last_reading > STATUS['setpoint'] + STATUS.get('tolerance', 0.5):
            fan_status = GPIO.HIGH
            GPIO.output(FAN_PIN, GPIO.HIGH)
        else:
            fan_status = GPIO.LOW
            GPIO.output(FAN_PIN, GPIO.LOW)

        if STATUS['fan'] != fan_status:
            STATUS['fan'] = fan_status
            mqtcc.publish(
                'myownbrewery/son_of_fermentation/fan', STATUS['fan'])

        time.sleep(15)

    GPIO.cleanup()
    mqtcc.disconnect()
