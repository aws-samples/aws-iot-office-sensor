# application.py
# Web application that retrieves data from an MQTT topic, populates a DynamoDB table with the data,
# and serves a web interface with streaming graphs.

# Import config file
import config

####
# DynamoDB #
import boto3

# Set configuration variables
region_name = config.REGION_NAME
aws_access_key_id = config.AWS_ACCESS_KEY_ID
aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY
table_name = config.TABLE_NAME
window = config.CALC_WINDOW

# Initialize database client
dynamodb = boto3.client("dynamodb", region_name=region_name, aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

# Initialize data structures
metrics_data = {}
anomalies = {}
####

####
# MQTT #
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from utils import *
import json

# Set configuration variables
data_topic = config.DATA_TOPIC

# Initialize MQTT client
client = AWSIoTMQTTClient('')

# Configure MQTT client
client.configureEndpoint(config.HOST_NAME, config.HOST_PORT)
client.configureCredentials(config.ROOT_CERT, config.PRIVATE_KEY, config.DEVICE_CERT)
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)


# Define callback to update data
def callback(client, userdata, message):
    global metrics_data, anomalies
    metric = str(message.topic.split('/')[2])
    data = history(dynamodb, table_name, metric, json.loads(message.payload)['ID'])
    stats = calculate_mas(metric, data, window)
    metrics_data[metric] = is_anomaly(stats)
    anomalies[metric] = metrics_data[metric][metrics_data[metric]['anomaly']]


# Connect
print('Connecting to endpoint ' + config.HOST_NAME)
client.connect()

# Subscribe to MQTT topic, trigger callback
print('Subscribing to "' + data_topic + '"')
client.subscribe(data_topic, 1, callback)
####

####
# Web Framework (Flask) #
from flask import Flask, render_template
from bokeh.embed import components

# Initialize Flask application
application = Flask(__name__)

x_label = "Time"


# render HTML web page
def render_metric(metric, unit):
    title = metric + ": Observations, Moving Averages, and Anomalies"
    metric_unit = metric + ", " + unit
    plot = plot_data(metrics_data[metric], anomalies[metric], title, x_label, metric_unit)
    script, div = components(plot)
    anomaly_data = anomalies[metric].to_dict()
    return render_template("index.html", metric=metric, data=anomaly_data, script=script, div=div)


@application.route('/')
@application.route('/temperature')
def temp():
    return render_metric("Temperature", "F")


@application.route('/pressure')
def press():
    return render_metric("Pressure", "mb")


@application.route('/humidity')
def humid():
    return render_metric("Humidity", "%")


if __name__ == '__main__':
    application.run(debug=True)

####
