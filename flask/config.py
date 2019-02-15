# config.py
# Define environment variables here

# AWS IoT endpoint settings
HOST_NAME = "your-aws-account-specific-prefix.iot.your-region.amazonaws.com"
HOST_PORT = 8883
PRIVATE_KEY = "certs/private.pem.key"
DEVICE_CERT = "certs/certificate.pem.crt"
ROOT_CERT = "certs/root-ca.cer"
REGION_NAME = "your-region"
AWS_ACCESS_KEY_ID = "your-access-key-id"
AWS_SECRET_ACCESS_KEY = "your-secret-access-key"

# DynamoDB settings
TABLE_NAME = "OfficeSensor"

# MQTT message settings
DATA_TOPIC = "office/metrics/#"

# Data processing settings
CALC_WINDOW = 10
