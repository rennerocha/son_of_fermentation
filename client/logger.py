# -*- coding: utf-8 -*-
import csv
import datetime

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    client.subscribe('myownbrewery/son_of_fermentation/temperature')
    client.subscribe('myownbrewery/son_of_fermentation/fan')
    client.subscribe('myownbrewery/son_of_fermentation/temperature/setpoint')


def on_disconnect(client, userdata, rc):
    pass


def on_message(client, userdata, message):
    if message.topic == 'myownbrewery/son_of_fermentation/temperature':
        log_data = True
        userdata['temperature'] = message.payload
    elif message.topic == 'myownbrewery/son_of_fermentation/temperature/setpoint':
        new_setpoint = message.payload
        log_data = userdata['setpoint'] != new_setpoint
        userdata['setpoint'] = new_setpoint
    elif message.topic == 'myownbrewery/son_of_fermentation/fan':
        new_fan_status = message.payload
        log_data = userdata['fan_status'] != new_fan_status
        userdata['fan_status'] = new_fan_status

    if log_data:
        now = datetime.datetime.now()
        LOG_FILE = 'SON_OF_FERMENTATION_{0}.log'.format(now.strftime('%Y-%m-%d'))

        fieldnames = ['datetime', 'temperature', 'setpoint', 'fan_status']
        with open(LOG_FILE, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': userdata.get('temperature', '0.0'),
                'setpoint': userdata.get('setpoint', '0.0'),
                'fan_status': userdata.get('fan_status', '0'),
            })


def start(mqtt_settings, running=True):
    userdata = {
        'setpoint': None,
        'temperature': None,
        'fan_status': None,
    }
    mqtcc = mqtt.Client('LOGGER', clean_session=False, userdata=userdata)

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
    mqtcc.loop_forever()
