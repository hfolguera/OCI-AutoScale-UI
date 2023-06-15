import os

# Flask configuration variables
DEBUG = True
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "")
SESSION_COOKIE_NAME = "OCIAutoScaleUI"
DEBUG_METRICS = 1

# App configuration variables
PREDEFINED_TAG = "Schedule"
#TOPIC
#LOG
#LOGLEVEL
ALLOW_START_STOP_RESOURCES = True

# Login configuration variable # TODO
LOGIN_REQUIRED = False
LOGIN_USERNAME = os.environ.get("FLASK_USERNAME", "")
LOGIN_PASSWORD = os.environ.get("FLASK_PASSWORD", "")

# REST URL
REST_URL = "https://g29dbebba3538cf-auto.adb.eu-madrid-1.oraclecloudapps.com/ords/automation/schedules/"