"""
Home Assistant Sensor Integration: Email Server Checker

This integration allows monitoring the status of IMAP and SMTP servers.
Provides real-time updates and notifications in case of connectivity issues.

License: MIT
Author: Theo van der Sluijs (tvdsluijs)
GitHub: https://github.com/tvdsluijs/hass_mail_server_checker
"""

from imaplib import IMAP4_SSL, IMAP4
from smtplib import SMTP_SSL, SMTPException
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST, CONF_PORT
import logging

# Logger setup
LOGGER = logging.getLogger(__name__)

# Constants
DEFAULT_IMAP_PORT = 993
DEFAULT_SMTP_PORT = 465

def setup_platform(hass, config, add_entities, discovery_info=None):
    """
    Set up the Email Server Checker sensors.

    Args:
        hass: Home Assistant instance.
        config: Sensor configuration from YAML.
        add_entities: Function to register sensor entities.
        discovery_info: Discovery data (not used here).
    """
    sensors = []
    for sensor_name, sensor_config in config["sensors"].items():
        sensors.append(
            MailServerChecker(
                sensor_name=sensor_name,
                friendly_name=sensor_config.get("friendly_name", sensor_name),
                imap_server=sensor_config["imap_server"],
                smtp_server=sensor_config["smtp_server"],
                username=sensor_config[CONF_USERNAME],
                password=sensor_config[CONF_PASSWORD],
                use_ssl=sensor_config.get("use_ssl", True),
            )
        )
    add_entities(sensors)


class MailServerChecker(Entity):
    """
    Sensor entity to monitor an IMAP and SMTP server.

    Attributes:
        sensor_name: Internal name for the sensor.
        friendly_name: User-friendly name displayed in the UI.
        imap_server: IMAP server details (host and port).
        smtp_server: SMTP server details (host and port).
        username: Login username for the email server.
        password: Login password for the email server.
        use_ssl: Boolean indicating whether to use SSL/TLS.
        state: Current state of the sensor ("OK" or error message).
        last_checked: ISO timestamp of the last successful or failed check.
    """

    def __init__(self, sensor_name, friendly_name, imap_server, smtp_server, username, password, use_ssl=True):
        self._sensor_name = sensor_name
        self._friendly_name = friendly_name
        self._imap_server = imap_server
        self._smtp_server = smtp_server
        self._username = username
        self._password = password
        self._use_ssl = use_ssl
        self._state = "Unknown"
        self._last_checked = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._friendly_name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """
        Return additional attributes for the sensor.

        Attributes include:
        - IMAP and SMTP server details.
        - Timestamp of the last check.
        """
        return {
            "imap_server": self._imap_server["host"],
            "smtp_server": self._smtp_server["host"],
            "last_checked": self._last_checked,
        }

    @property
    def icon(self):
        """Return an icon based on the current state."""
        return "mdi:check-circle" if self._state == "OK" else "mdi:alert-circle"

    def update(self):
        """
        Perform the IMAP and SMTP checks and update the sensor state.

        The method:
        - Connects to the IMAP server to validate credentials.
        - Connects to the SMTP server to validate credentials.
        - Updates the state and logs any errors.
        """
        try:
            # Check IMAP
            self._check_imap()
            # Check SMTP
            self._check_smtp()

            # If both checks succeed
            self._state = "OK"
        except Exception as e:
            # Log the error and update state
            LOGGER.error(f"Mail server check failed for {self._friendly_name}: {e}")
            self._state = f"Error: {str(e)}"
        finally:
            # Record the last check timestamp
            self._last_checked = datetime.now().isoformat()

    def _check_imap(self):
        """Check IMAP server connectivity."""
        try:
            LOGGER.debug(f"Connecting to IMAP server: {self._imap_server['host']}")
            imap_conn = IMAP4_SSL(self._imap_server["host"], self._imap_server.get("port", DEFAULT_IMAP_PORT))
            imap_conn.login(self._username, self._password)
            imap_conn.logout()
            LOGGER.debug(f"IMAP server check successful for: {self._imap_server['host']}")
        except IMAP4.error as imap_err:
            raise Exception(f"IMAP Error: {imap_err}")

    def _check_smtp(self):
        """Check SMTP server connectivity."""
        try:
            LOGGER.debug(f"Connecting to SMTP server: {self._smtp_server['host']}")
            smtp_conn = SMTP_SSL(self._smtp_server["host"], self._smtp_server.get("port", DEFAULT_SMTP_PORT))
            smtp_conn.login(self._username, self._password)
            smtp_conn.quit()
            LOGGER.debug(f"SMTP server check successful for: {self._smtp_server['host']}")
        except SMTPException as smtp_err:
            raise Exception(f"SMTP Error: {smtp_err}")
