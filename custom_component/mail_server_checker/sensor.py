import imaplib
import smtplib
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST, CONF_PORT

def setup_platform(hass, config, add_entities, discovery_info=None):
    sensors = []
    for sensor_name, sensor_config in config["sensors"].items():
        sensors.append(
            MailServerChecker(
                sensor_name,
                sensor_config["friendly_name"],
                sensor_config["imap_server"],
                sensor_config["smtp_server"],
                sensor_config[CONF_USERNAME],
                sensor_config[CONF_PASSWORD],
            )
        )
    add_entities(sensors)

class MailServerChecker(Entity):
    def __init__(self, sensor_name, friendly_name, imap_server, smtp_server, username, password):
        self._sensor_name = sensor_name
        self._friendly_name = friendly_name
        self._imap_server = imap_server
        self._smtp_server = smtp_server
        self._username = username
        self._password = password
        self._state = "Unknown"

    @property
    def name(self):
        return self._friendly_name

    @property
    def state(self):
        return self._state

    def update(self):
        try:
            # IMAP Check
            imap_conn = imaplib.IMAP4_SSL(self._imap_server["host"], self._imap_server["port"])
            imap_conn.login(self._username, self._password)
            imap_conn.logout()

            # SMTP Check
            smtp_conn = smtplib.SMTP_SSL(self._smtp_server["host"], self._smtp_server["port"])
            smtp_conn.login(self._username, self._password)
            smtp_conn.quit()

            self._state = "OK"
        except Exception as e:
            self._state = f"Error: {str(e)}"
