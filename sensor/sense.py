# Simple application that periodically collects sensor data from a Raspberry Pi SenseHat and sends the data to the
# AWS MQTT broker with the AWS MQTT client API

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from sense_hat import SenseHat
import config
import time
import json
from datetime import datetime

sense = SenseHat()
sense.clear()


# Define function to collect weather data
def get_weather(id):
    temperature = float(sense.get_temperature() * (9 / 5) + 32)
    humidity = float(sense.get_humidity())
    pressure = float(sense.get_pressure())
    timestamp = str(datetime.now())
    weather = {'ID': id, 'Temperature': temperature, 'Humidity': humidity, 'Pressure': pressure, 'Timestamp': timestamp}
    return weather


# Define variable for MQTT topic from config file
sensor_topic = config.SENSOR_TOPIC

# Initialize MQTT client
client = AWSIoTMQTTClient('')

# Configure client endpoint, port information, certs
client.configureEndpoint(config.HOST_NAME, config.HOST_PORT)
client.configureCredentials(config.ROOT_CERT, config.PRIVATE_KEY, config.DEVICE_CERT)
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)

# Connect
print('Connecting to endpoint ' + config.HOST_NAME)
client.connect()

# Loop through metrics, publish every 15 seconds
id = 0
metrics = ['Temperature', 'Humidity', 'Pressure']
while True:
    for metric in metrics:
        data = {key: get_weather(id)[key] for key in (metric, 'ID', 'Timestamp')}
        sub_topic = sensor_topic.split('/')[0] + '/metrics/' + metric
        client.publish(sub_topic, json.dumps(data), config.QOS_LEVEL)
        print('The ' + metric + ' on the 8th floor of LowFlyingHawk is ' + str(data[metric]) + '. Published message on '
                                                                                               'topic ' + sub_topic)
    client.publish(sensor_topic, json.dumps(get_weather(id)), config.QOS_LEVEL)
    print('Published message on topic ' + sensor_topic)
    id += 1
    time.sleep(15)
