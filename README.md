# Email Server Checker

Monitor the status of your IMAP and SMTP email servers directly within Home Assistant.

## Features
- Check multiple IMAP and SMTP servers.
- Real-time error reporting as sensor states.
- SSL/TLS support for secure connections.
- Full integration with Home Assistant automations and notifications.

## Configuration
Add the following to your `configuration.yaml` to set up the integration:

```yaml
sensor:
  - platform: email_checker
    unique_id: "email_server_check_1"
    name: "Server 1 Status"
    imap_server:
      host: imap.example.com
      port: 993
    smtp_server:
      host: smtp.example.com
      port: 465
    username: "your_email@example.com"
    password: "your_password"
```
You can add multiple servers by creating additional sensor entries.

## Automation Example

Use the following automation to check your email servers hourly and notify you if there’s an issue:

```yaml
automation:
  - alias: "Check Email Servers Hourly"
    trigger:
      - platform: time_pattern
        minutes: "/60"
    action:
      - service: homeassistant.update_entity
        target:
          entity_id:
            - sensor.email_server_check_1
            - sensor.email_server_check_2
      - condition: template
        value_template: >
          {{ 'error' in states('sensor.email_server_check_1').lower() or
             'error' in states('sensor.email_server_check_2').lower() }}
      - service: notify.mobile_app_iphone_van_theo
        data:
          title: "Email Server Error"
          message: >
            Server 1: {{ states('sensor.email_server_check_1') }}
            Server 2: {{ states('sensor.email_server_check_2') }}
```

## Why Use This Integration?

Keeping your email servers online and functional is crucial for communications. With this integration, you can:
	•	Monitor availability in real-time.
	•	React to server downtime with Home Assistant automations.
	•	Gain peace of mind knowing your email infrastructure is monitored.

## Get Started

Install this integration through HACS or manually download it from GitHub. Follow the configuration steps to get started!
