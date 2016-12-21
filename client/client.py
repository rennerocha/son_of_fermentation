#!/usr/bin/python
from threading import Thread

import logger
import son_of_fermentation


MQTT_BROKER_HOST = 'broker.myownbrewery.com'
MQTT_BROKER_PORT = 8883
MQTT_BROKER_USERNAME = 'xxx'
MQTT_BROKER_PASSWORD = 'xxx'


def main():
    mqtt_settings = {
        'host': MQTT_BROKER_HOST,
        'port': MQTT_BROKER_PORT,
        'username': MQTT_BROKER_USERNAME,
        'password': MQTT_BROKER_PASSWORD,
    }
    logger_thread = Thread(target=logger.start, args=(mqtt_settings, ))
    logger_thread.start()

    sof_thread = Thread(target=son_of_fermentation.start, args=(mqtt_settings, ))
    sof_thread.start()


if __name__ == '__main__':
    main()
