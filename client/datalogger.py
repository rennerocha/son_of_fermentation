import paho.mqtt.client as mqtt

import environment


def on_connect(client, userdata, flags, rc):
    client.subscribe('temperaturemonitor/sensors/#')
    client.subscribe('temperaturemonitor/actuators/#')


def on_message(client, userdata, msg):
    _, _, subject_name = msg.topic.split('/')
    subject_value = msg.payload
    with open('{0}.csv'.format(subject_name), 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            subject_value
        ])


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(environment.BROKER_USERNAME, environment.BROKER_PASSWORD)
client.connect(environment.BROKER_HOST, environment.BROKER_PORT)
client.loop_forever()

