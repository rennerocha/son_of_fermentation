#!/usr/bin/python
import csv
import datetime
import requests
import time
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor


FAN_PIN = 7
TEMPERATURE_SET_POINT = 17


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

    with open('son_of_fermentation.csv', 'a') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            temperature,
            fan_status,
        ])


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, GPIO.LOW)

    fan_status = GPIO.LOW
    sensor = W1ThermSensor()
    while True:
        actual_temperature = sensor.get_temperature()
        if actual_temperature > TEMPERATURE_SET_POINT:
            fan_status = GPIO.HIGH
            interval = 5
            GPIO.output(FAN_PIN, GPIO.HIGH)
        else:
            fan_status = GPIO.LOW
            interval = 30
            GPIO.output(FAN_PIN, GPIO.LOW)

        log_reading(actual_temperature, fan_status)
        time.sleep(interval)

    GPIO.cleanup()


if __name__ == '__main__':
    time.sleep(10)  # wait for internet
    main()

