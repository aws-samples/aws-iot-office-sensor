# config.py

# AWS IoT endpoint settings
HOST_NAME = "your-aws-account-specific-prefix.iot.your-region.amazonaws.com"
HOST_PORT = 8883

# Thing certs & keys
PRIVATE_KEY = "certs/private.pem.key"
DEVICE_CERT = "certs/certificate.pem.crt"
ROOT_CERT = "certs/root-CA.crt"

# Message settings
SENSOR_TOPIC = "office/weather"
QOS_LEVEL = 0
