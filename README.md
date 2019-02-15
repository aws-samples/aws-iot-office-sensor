# AWS IoT Use Case: Monitoring the Office Climate
## Overview
If you're new to IoT and you want to start analyzing real-time data, the weather is a great place to start. In this example, we use a Raspberry Pi Sense HAT and AWS services to monitor weather patterns in the office. Two parts make up the example:
* An Office Sensor Application
* A Web Application

## [Office Sensor Application](/sensor/)
The Office Sensor application pulls weather data from a Raspberry Pi Sense HAT and publishes the data to MQTT topics served by the AWS IoT MQTT Broker. An AWS IoT Core rule sends the data published to the office's weather topics to an AWS IoT Analytics channel for further analysis.

See the [`sensor`](/sensor/) directory for more information about the office sensor application.

## [Web Application](/flask/)
A separate AWS IoT Core rule sends the weather data to an AWS DynamoDB table for storage. A Flask application listens to the office's weather topics for updates, and populates tables and charts in a web page with descriptive statistics on real-time and historical data.

See the [`flask`](/flask/) directory for more information about the web application.
